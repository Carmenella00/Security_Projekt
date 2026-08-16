# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Ubuntu Server 24.04 LTS
  config.vm.box = "bento/ubuntu-24.04"

  # Gemeinsame Basiskonfiguration
  common_provisioning = <<-SHELL
    export DEBIAN_FRONTEND=noninteractive

    # Zeitzone und Zeitsynchronisation
    timedatectl set-timezone Europe/Zurich
    timedatectl set-ntp true

    apt-get update
    apt-get upgrade -y

    apt-get install -y \
      ca-certificates \
      curl \
      gnupg \
      apt-transport-https

    apt-get autoremove -y
    apt-get autoclean -y
  SHELL

  # ------------------------------------------------------------
  # InfluxDB 2
  # ------------------------------------------------------------
  config.vm.define "influxdb" do |influxdb|
    influxdb.vm.hostname = "influxdb"

    # InfluxDB auf dem Host über localhost:8086 erreichbar
    influxdb.vm.network "forwarded_port",
      guest: 8086,
      host: 8086,
      host_ip: "127.0.0.1",
      auto_correct: true

    # Parallels
    influxdb.vm.provider "parallels" do |prl|
      prl.name = "influxdb"
      prl.memory = 2048
      prl.cpus = 2
    end

    # VirtualBox
    influxdb.vm.provider "virtualbox" do |vb|
      vb.name = "influxdb"
      vb.memory = 2048
      vb.cpus = 2
    end

    influxdb.vm.provision "shell", inline: common_provisioning

    influxdb.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive

      curl --silent --location \
        https://repos.influxdata.com/influxdata-archive.key \
        -o /tmp/influxdata-archive.key

      gpg --dearmor \
        --yes \
        --output /usr/share/keyrings/influxdata-archive.gpg \
        /tmp/influxdata-archive.key

      echo "deb [signed-by=/usr/share/keyrings/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main" \
        > /etc/apt/sources.list.d/influxdata.list

      apt-get update
      apt-get install -y influxdb2

      systemctl enable influxdb
      systemctl restart influxdb

      echo "InfluxDB wurde installiert."
      echo "Erreichbar unter: http://localhost:8086"
    SHELL
  end

  # ------------------------------------------------------------
  # Grafana
  # ------------------------------------------------------------
  config.vm.define "grafana" do |grafana|
    grafana.vm.hostname = "grafana"

    # Grafana auf dem Host über localhost:3000 erreichbar
    grafana.vm.network "forwarded_port",
      guest: 3000,
      host: 3000,
      host_ip: "127.0.0.1",
      auto_correct: true

    # Parallels
    grafana.vm.provider "parallels" do |prl|
      prl.name = "grafana"
      prl.memory = 2048
      prl.cpus = 2
    end

    # VirtualBox
    grafana.vm.provider "virtualbox" do |vb|
      vb.name = "grafana"
      vb.memory = 2048
      vb.cpus = 2
    end

    grafana.vm.provision "shell", inline: common_provisioning

    grafana.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive

      mkdir -p /etc/apt/keyrings

      curl --silent --show-error \
        https://apt.grafana.com/gpg.key |
        gpg --dearmor \
          --yes \
          --output /etc/apt/keyrings/grafana.gpg

      echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" \
        > /etc/apt/sources.list.d/grafana.list

      apt-get update
      apt-get install -y grafana

      systemctl daemon-reload
      systemctl enable grafana-server
      systemctl restart grafana-server

      echo "Grafana wurde installiert."
      echo "Erreichbar unter: http://localhost:3000"
    SHELL
  end
end