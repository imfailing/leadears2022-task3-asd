PGDMP                     
    z            my_local_postgres    15.0    15.0                0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false                       1262    16398    my_local_postgres    DATABASE     �   CREATE DATABASE my_local_postgres WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
 !   DROP DATABASE my_local_postgres;
                postgres    false            �            1259    77551    address_catalog    TABLE     �   CREATE TABLE public.address_catalog (
    addr_id bigint,
    okrug text,
    raion text,
    location text,
    latitude numeric(8,6),
    longitude numeric(9,6)
);
 #   DROP TABLE public.address_catalog;
       public         heap    postgres    false            �            1259    70559 
   full_table    TABLE     o  CREATE TABLE public.full_table (
    root_request_id bigint NOT NULL,
    request_version_id bigint,
    request_num text,
    mosru_num text,
    created_ts timestamp with time zone,
    version_eff_start_ts text,
    data_source_name text,
    data_source_code text,
    creator_name text,
    incident_flg text,
    root_parent_id numeric,
    parent_code text,
    modified_user_name text,
    user_organization_role text,
    comments text,
    defect_cat_name text,
    defect_cat_root_id bigint,
    defect_cat_code text,
    defect_name text,
    defect_short_name text,
    defect_id bigint,
    defect_code text,
    defect_redo_flg text,
    description text,
    user_question text,
    urgency_cat_name text,
    urgency_cat_code text,
    entrance text,
    floor text,
    apartment text,
    "ODS" text,
    management_comp_name text,
    service_comp_name text,
    service_comp_id numeric,
    service_comp_inn numeric,
    request_status_name text,
    request_status_code text,
    service_refuse_reason text,
    service_refuse_reason_id numeric,
    service_comp_refuse_reason text,
    service_comp_refuse_reason_id numeric,
    job_type text,
    job_type_root_id text,
    materials_used text,
    protection_name text,
    protection_root_id text,
    effectiveness text,
    effectiveness_code text,
    retry_count numeric,
    last_retry_date text,
    is_retrying_flg text,
    is_notified_flg text,
    closed_date timestamp with time zone,
    desired_start_low_ts timestamp with time zone,
    desired_start_high_ts timestamp with time zone,
    review_date text,
    quality_rate text,
    quality_rate_code text,
    payment_cat_name text,
    payment_cat_id text,
    is_card_flg text,
    diff_time numeric,
    rule_one boolean,
    rule_two boolean,
    rule_four boolean,
    rule_five boolean,
    addr_id bigint,
    review_id bigint,
    rule_three boolean
);
    DROP TABLE public.full_table;
       public         heap    postgres    false            �            1259    77942 	   mood_data    TABLE     �   CREATE TABLE public.mood_data (
    root_request_id bigint,
    mood_id bigint,
    created_ts timestamp with time zone,
    latitude numeric(8,6),
    longitude numeric(9,6)
);
    DROP TABLE public.mood_data;
       public         heap    postgres    false            �            1259    77921    people_mood    TABLE     w   CREATE TABLE public.people_mood (
    review_id bigint NOT NULL,
    mood_id bigint,
    mood text,
    review text
);
    DROP TABLE public.people_mood;
       public         heap    postgres    false            �            1259    77558    search_data    TABLE       CREATE TABLE public.search_data (
    root_request_id bigint,
    defect_cat_name text,
    request_num text,
    problem_address text,
    defect_cat_root_id bigint,
    created_ts date,
    address_lat numeric(8,6),
    address_long numeric(9,6),
    is_problem_flg boolean
);
    DROP TABLE public.search_data;
       public         heap    postgres    false            u           2606    70565    full_table full_table_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY public.full_table
    ADD CONSTRAINT full_table_pkey PRIMARY KEY (root_request_id);
 D   ALTER TABLE ONLY public.full_table DROP CONSTRAINT full_table_pkey;
       public            postgres    false    214            z           2606    77927    people_mood people_mood_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.people_mood
    ADD CONSTRAINT people_mood_pkey PRIMARY KEY (review_id);
 F   ALTER TABLE ONLY public.people_mood DROP CONSTRAINT people_mood_pkey;
       public            postgres    false    217            w           1259    77899    problem_index    INDEX     f   CREATE INDEX problem_index ON public.search_data USING btree (is_problem_flg) WITH (fillfactor='90');
 !   DROP INDEX public.problem_index;
       public            postgres    false    216            v           1259    77564    root_id_index    INDEX     s   CREATE INDEX root_id_index ON public.full_table USING btree (root_request_id, request_num) WITH (fillfactor='90');
 !   DROP INDEX public.root_id_index;
       public            postgres    false    214    214            x           1259    77567    search_index    INDEX     �   CREATE INDEX search_index ON public.search_data USING btree (address_lat, address_long, created_ts, defect_cat_name) WITH (fillfactor='90');
     DROP INDEX public.search_index;
       public            postgres    false    216    216    216    216           