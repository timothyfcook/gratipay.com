BEGIN;

    ALTER TABLE elsewhere ALTER COLUMN user_name DROP NOT NULL;

END;
