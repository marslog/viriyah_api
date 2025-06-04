# variables.tf
variable "access_key" {}
variable "secret_key" {}
variable "scp_ip" {}
variable "az_id" {}
variable "location_id" {}
variable "storage_tag_id" {}
variable "image_id" {}
variable "cores" { default = 2 }
variable "sockets" { default = 1 }
variable "memory_mb" { default = 4096 }
variable "boot_order" { default = "cd" }
variable "disk_size_mb" { default = 81920 }
variable "vif_id" {}
