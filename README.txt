# Hautdebit-PRS PROJET

Hautdebit est un projet Python qui créer un server pour gerer la transmission du fichier au client particulier via le protocol UDP et des mecanismes de la gestion du controle

## Auteur
Ngo Tuan Kiet
Oussama Garaaoui


## Prérequis
Tous les programmes sont ecrits en Python3, donc il faux avoir un environnement Python3 pour les lancer

## Lancement
(TOUS LES FICHIERS A TRANSMETTRE SONT DANS LE DOSSIER "SRC", SANS LEQUEL, LE SERVEUR NE TROUVE PAS LES FICHIERS ) 
 
( SI VOUS VOULEZ TESTER VOTRE FICHIER, LE METTEZ DANS LE DOSSIER "SRC" )

Trouvez-vous dans le dossier "src" et choisissez-vous un fichier pour lancer
Au serveur:
* Pour client1
```python3 server1-HautDebit.py <Numero_du_port>
```
* Pour client2
```python3 server2-HautDebit.py <Numero_du_port>
```
*Pour multiclient
```python3 multiclient-HautDebit.py <Numero_du_port>
```
Au client:
``` ./clientX IPServeur NuméroPortServeur NomFichier 0
```
Exemple :
``` ./client1 134.214.202.237 8000 12mb.pdf 0
```
-, IPServeur: l'addresse du IP du serveur
-, NuméroPortServeur: Le numéro du port serveur
-, NomFichier: le nom des fichiers exitants dans le dossier "ressouce".
On vous conseille de choisir le fichier "12mb.pdf", pour ne pas prendre plus du temps de la transmission


## Description
Le project contient :
-, Un dossier "src" contenant tous les principaux codes Python exécutables du projet
-, Un dossier "venv" est une bibliothèque racine du Python3
-, Un dossier "pres" contenant le support de présentation de projet
** Remarque:
Dans tous les codes du serveur, on met le timeout du socket UDP principal à 40s, le timeout du socket UDP secondaire à 20s (pour le multiclient)
Alors, meme si le client termine, il faux attendre le timeout pour arreter le serveur ainsi que le program.
Pour changer ce parametre, trouvez-vous dans la fonction "def handshake()" et changez le valeur du timeout dans la function "self.sock.settimeout(20)"


## FIN
