# main.tf
provider "null" {}

resource "null_resource" "generate_vm" {
  provisioner "local-exec" {
    command = <<EOT
      python3 create_vm.py
    EOT
  }
}
