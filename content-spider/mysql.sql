drop database weibo;
create database weibo charset utf8;
use weibo;

create table user(
	url					varchar(30)               primary key ,
	email					varchar(50) 			,
	username 				varchar(30)				not null,
	gender					int(1)					,
        dz                                      varchar(10),
	introduct				varchar(50)				default 'no',
	birth				      char(30)				,
	vip                                    int(1)                          ,
        fan                                      int(15),
        wb_num                                    int(10)
);

create table wb(
	id						int 					primary key auto_increment,
	url					varchar(30) 					not null,
        zf                                      int                                     not null,
        pl                                      int                                     not null,
        dz                                      int                                     not null,
	content					text					not null,
	foreign key (url) references user(url)
);
