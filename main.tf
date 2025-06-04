# main.tf
provider "sangfor" {
  access_key = var.access_key
  secret_key = var.secret_key
  scp_host   = var.scp_ip
}

resource "sangfor_vm" "windows_vm" {
  name            = "win_vm_iso_fixed"
  az_id           = var.az_id
  location_id     = var.location_id
  storage_tag_id  = var.storage_tag_id
  image_id        = var.image_id

  cores           = var.cores
  sockets         = var.sockets
  memory_mb       = var.memory_mb
  boot_order      = var.boot_order

  disk {
    id          = "ide0"
    type        = "new_disk"
    preallocate = false
    size_mb     = var.disk_size_mb
  }

  network {
    vif_id   = var.vif_id
    connect  = true
    model    = "virtio"
  }

  power_on = false
}
