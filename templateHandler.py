import jinja2

def render_template(template_name, args):
    template_dir = 'templates'
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader)
    templates = template_env.list_templates()
    template = template_env.get_template(template_name)
    return template.render(args)