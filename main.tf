# main.tf

provider "null" {}

resource "null_resource" "create_vm_with_python" {
  provisioner "local-exec" {
    command = "python3 create_vm.py"
  }
}
