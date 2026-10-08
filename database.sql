-- Script de creación de base de datos para PostgreSQL

-- 1. Crear base de datos (Ejecutar este comando primero en postgres, luego conectarse a ella)
-- CREATE DATABASE flora_fauna_puebla;
-- \c flora_fauna_puebla;

CREATE TABLE especies (
    id SERIAL PRIMARY KEY,
    nombre_comun VARCHAR(100) NOT NULL,
    nombre_cientifico VARCHAR(150),
    tipo VARCHAR(50) CHECK (tipo IN ('Flora', 'Fauna')),
    descripcion TEXT,
    habitat VARCHAR(255),
    endemica BOOLEAN DEFAULT false
);

CREATE TABLE detecciones_usuarios (
    id SERIAL PRIMARY KEY,
    especie_id INTEGER REFERENCES especies(id),
    imagen_path VARCHAR(255) NOT NULL,
    nivel_confianza NUMERIC(5, 2),
    fecha_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    plataforma VARCHAR(50) -- 'Mobile' o 'Web'
);

-- Algunos datos de ejemplo para Puebla
INSERT INTO especies (nombre_comun, nombre_cientifico, tipo, descripcion, habitat, endemica) 
VALUES 
('Cacomixtle', 'Bassariscus astutus', 'Fauna', 'Mamífero omnívoro nocturno, cola anillada, trepador ágil.', 'Bosques y zonas urbanas', false),
('Encino', 'Quercus rugosa', 'Flora', 'Árbol característico de los bosques templados de la región.', 'Bosques de pino-encino', false),
('Ajolote del Altiplano', 'Ambystoma velasci', 'Fauna', 'Anfibio endémico de la región central, habita en cuerpos de agua.', 'Cuerpos de agua lentos', true);
