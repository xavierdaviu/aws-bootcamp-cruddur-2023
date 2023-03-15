-- this file was manually created
INSERT INTO public.users (display_name, handle, cognito_user_id, email)
VALUES
  ('Andrew Brown', 'andrewbrown' ,'MOCK', 'ab2@c.com'),
  ('Andrew Bayko', 'bayko' ,'MOCK', 'ab2@c.com');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'andrewbrown' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
