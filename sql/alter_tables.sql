-- Migration: Make cart user-specific by adding user_id column
-- Run this after your existing tables are created

-- Add user_id column to cart table
ALTER TABLE cart ADD COLUMN user_id INT NOT NULL DEFAULT 1 AFTER id;

-- Add foreign key constraint
ALTER TABLE cart ADD CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Update the unique constraint so each user can have their own cart entry per item
-- First drop existing entries to avoid duplicates, then add unique constraint
ALTER TABLE cart ADD UNIQUE KEY unique_user_item (user_id, item_id);
