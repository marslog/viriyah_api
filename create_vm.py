import hashlib
import hmac
import requests
import datetime
import json
from pprint import pprint

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    return sign(kService, 'aws4_request')

def aws4_post(path, scp_ip, access_key, secret_key, payload):
    method = 'POST'
    service = 'open-api'
    region = 'cn-south-1'
    endpoint = f'https://{scp_ip}{path}'
    content_type = 'application/json'

    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')

    request_body = json.dumps(payload)
    payload_hash = hashlib.sha256(request_body.encode('utf-8')).hexdigest()

    canonical_headers = (
        f'content-type:{content_type}\n'
        f'host:{scp_ip}\n'
        f'x-amz-content-sha256:{payload_hash}\n'
        f'x-amz-date:{amz_date}\n'
    )
    signed_headers = 'content-type;host;x-amz-content-sha256;x-amz-date'

    canonical_request = f"{method}\n{path}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    signing_key = getSignatureKey(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = (
        f'{algorithm} Credential={access_key}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, Signature={signature}'
    )

    headers = {
        'Content-Type': content_type,
        'X-Amz-Date': amz_date,
        'X-Amz-Content-Sha256': payload_hash,
        'Authorization': authorization_header
    }

    try:
        res = requests.post(endpoint, headers=headers, data=request_body, verify=False)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"\n❌ POST request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return None

def load_config():
    try:
        with open("terraform.tfvars") as f:
            config = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"')
            return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return None

def generate_vm_payload():
    return {
          "az_id": "9d5d56c1-10bb-45ba-9862-acf2bd4bcf64",
        "location": {
            "id": "cluster"
        },
        "storage_tag_id": "11111111-1111-1111-1111-111111111111",
        "image_id": "fbecf65e-fda0-4b55-bbdf-aac1034cd89e",
        "cores": 1,
        "sockets": 1,
        "memory_mb": 1024,
        "count": 1,
        "name": "terraform_wasin",
        "description": "",
        "advance_param": {
            "boot_order": "c",
            "onboot": 0,
            "schedopt": 0,
            "abnormal_recovery": 1,
            "cpu_hotplug": 0,
            "mem_hotplug": 0,
            "balloon_memory": 0,
            "hugepage_memory": 0
        },
        "disks": [
            {
            "id": "ide0",
            "type": "derive_disk",
            "preallocate": 0,
            "size_mb": 81920
            }
        ],
        "networks": [
            {
            "vif_id": "net0",
            "connect": 1,
            "model": "virtio",
            "host_iso": 0,
            }
        ],
        "power_on": 0
        }


def write_payload_to_file(payload, filename="payload.json"):
    try:
        with open(filename, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"\n✅ {filename} created successfully.")
    except IOError as e:
        print(f"\n❌ Failed to write payload to file {filename}: {e}")

if __name__ == "__main__":
    config = load_config()
    if not config:
        print("Failed to load configuration. Please check terraform.tfvars file.")
        exit(1)

    access_key = config.get("access_key")
    secret_key = config.get("secret_key")
    scp_ip = config.get("scp_ip")

    if not all([access_key, secret_key, scp_ip]):
        print("Missing required configuration in terraform.tfvars")
        exit(1)

    vm_payload = generate_vm_payload()
    write_payload_to_file(vm_payload)

    print("\n--- Creating VM ---")
    response = aws4_post("/janus/20180725/servers", scp_ip, access_key, secret_key, vm_payload)
    if response:
        print("\n✅ VM Created Successfully:")
        print(json.dumps(response, indent=2))
    else:
        print("\n❌ VM creation failed.")
