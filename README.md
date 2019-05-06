## Item catalog web app built in Python

This is a web application built on the Python Flask framework that allows users to add items under categories. Categories are managed by admin users.

## Features

1. Sign in with Google account.
2. Users can add items under different categories.
3. Users can update and delete their own items.
4. Role based permission system. We currently have admin users and normal users.
5. The backend administrator can add admin users who can add, edit, update categories and all items.
6. Local permission system that restricts users from deleting or updating other users' items.
7. Admin users are allowed to update and delete any item of any user.


Uses Bootstrap for some components.


## Setting up

Download the file named `Vagrantfile`, available in this repository, into a directory.


### Installing the virtual machine (optional)

**It is up to you to run the web app without using a virtual machine, but I recommend using the virtual machine to avoid making unwanted changes to your system.**


Cd into the directory containing the `Vagrantfile`. And then run

`$ vagrant up`

This requires Vagrant and VirtualBox to be already installed on your system.

The command will install an Ubuntu 18.04 virtual machine on your system. It can take some time depending on your connection speed.

### Connect to the virtual machine

Your virtual machine should be running now. To connect to it, run `vagrant ssh`

### Logging out and in to your VM

To log out of your virtual machine, run type `CTRL+D`. To stop the running vm, run
`vagrant halt`.

If you reboot your computer, or you have stopped your virtual machine, start it again by running `vagrant up` the same way as you did before. Note: This will not download the virtual machine again from the network.



### Install dependencies
Once you are in the vm, install the dependencies with the following commands.


    sudo apt update
    sudo apt install git
    sudo apt-get install postgresql postgresql-contrib
    sudo apt install python3
    sudo apt install python3-pip

    sudo pip3 install flask
    sudo pip3 install sqlalchemy

Psycopg2

    sudo apt install libpq-dev python3-dev
    sudo pip3 install psycopg2

Google signin api

    sudo pip3 install --upgrade google-api-python-client


## Clone the repository

While you're connected to your virtual machine, run the following command.

`$ cd /home/vagrant`

Then run the following command to clone the repository in this directory. You can also use any directory that you want.


`$ git clone https://github.com/davidaik/item-catalog.git`



## Setting up the database

This web app uses a Postgresql database to store data.

Let's set it up.

While connected to the VM, run the following commands to set up a new user for Postgres.

We are using user name `catuser` and password `catalog` as an example.

    sudo -i -u postgres
    createuser --interactive -P
    Enter name of role to add: catuser
    Enter password for new role: 
    Enter it again:
    Shall the new role be a superuser? (y/n) y
    
Then open the Postgres console by running the command `psql`. We will be creating our database in this console.

Once connected, run the following commands.

    create database catalog;
    grant all privileges on database catalog to catuse;

Then press CTRL+D and then CTRL+D again, to exit the Postgres console and then log out of the Postgres user.


If you have used your own role name, password or database name, you will need to update the following line in your `db_init.py` file.

    'postgresql+psycopg2://catuser:catalog@localhost/catalog'

The syntax for this line is

    'postgresql+psycopg2://role_name:role_password@localhost/databse_name'



## Get Google API key

We need a Google API key for Google signin to work on our web app.

Get it from [Here](https://developers.google.com/identity/sign-in/web/sign-in) or [Here](https://console.developers.google.com)

While setting up your project there, use `http://localhost:8000` as the allowed JavaScript origin.

Once you have a client id, you will need to update the `server.py` file to add it.

## Usage

Once everything is set up, we can start the server. But before that, let's add an admin user's email so that we can set up categories for the website. The `addmin.py` is used to manage admin users.

    python3 addmin.py
    There are currently no admins.
    Enter new admin Gmail address: 

Enter the **Gmail** address of the user who will act as the admin.

Once we have an admin user, we can start the server.

    python3 server.py

Once the server is running, we can connect to the home page at http://localhost:8000

## JSON endpoints

The app has two json endpoints

    http://localhost:8000/items.json

This gives us all items in the database in JSON format.

The other endpoint gives data of an item in JSON format.

    http://localhost:8000/item.json?id=ITEM_ID

Here, ITEM_ID could be any integer but it should exist in the database.


## License
> MIT License

> Copyright (c) 2019 David Heisnam

> Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software withouta copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

> The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.