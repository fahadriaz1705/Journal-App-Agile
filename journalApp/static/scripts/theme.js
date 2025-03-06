let p_c = "{{user.theme.primary_color}}";
let s_c = "{{user.theme.secondary_color}}"; 
let t_c = "{{user.theme.tertiary_color}}";
document.documentElement.style.setProperty('--primary_color', p_c);
document.documentElement.style.setProperty('--secondary_color', s_c);
document.documentElement.style.setProperty('--tertiary_color', t_c);