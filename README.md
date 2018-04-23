# Catalog

Catalog is a project by Udacity FullStack Web Developer Nanodegree. In this project, we can add, edit and delete games, if you're loged in, in differents categories.


### Tech

Catalog uses the following tools:
  - [Python 2.7](https://www.python.org/downloads/) 
  - [Vagrant - current version 2.0.2](https://www.vagrantup.com/)
  - [Oracle VM VirtualBox](https://www.virtualbox.org/)
  - Code editor - like [Sublime Text](https://www.sublimetext.com/) or others
  - Terminal / you can also use [Git Bash](https://git-scm.com/) 


### Requirements:

  - Knowlodge in Python
  - Knowlodge in Flask
  - Knowlodge in SQL Alchemy
  - Knowlodge in Git
  - Git directory: fullstacl-nanodegree-vm 

### Installation

#### Install Virtual Box

Install the platform package for your operating system. You do not need the extension pack. You do not need to launch VirtualBox after installing it.

#### Install Vagrant

Vagrant is the software that configures the VM and let share files between your host computer and the Virtual Machine System. Install the version for your operating system.
For Windows users: allow the firwall exception

#### Download VM Configuration 

The [repository](https://github.com/udacity/fullstack-nanodegree-vm) can be forked and cloned in GitHub. 
Alternately, you can download and unzip this [file](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip)

In your terminal, change to this directory with the comand:
```sh
$ cd 
```

Inside you will find another directory called vagrant. Change directory to vagrant directory

```sh
$ cd vagrant
```

#### Start the virtual machine

inside the vagrant subdirectory, run the command:
```sh
$ vagrant up
```
This will cause Vagrant to download the Linux operating system and install it.

When vagrant up is finished running, you will get your shell prompt back. At this point, you can run:
```sh
$ vagrant ssh
```
This comand log in to your Linux Virtual Machine.

Now, you're logged in! The shell prompt should starts with the word vagrant.

#### Project File

Inside the VM, change directory to: 
```sh
$ cd /vagrant 
```
And look around with: 
```sh
$ ls
```
The files are the same as the ones in the vagrant subdirectory on your computer.

#### Database 

You must set the database with the command:
```sh
$ python database_setup.py
``` 


### Project Files

For answer this questions, the project contains the file ```catalog.py```. This file must be in the same vagrant directory, together to the ```database_setup.py``` file.


### Run

For run this project in your virtual machine, in your terminal, use ```cd``` to the vagrant directory and type:
```sh
python catalog.py
```

And the localhost is already running in your machine. 

Open your browser and type ```http://localhost:8000``` and you can access the catalog.

