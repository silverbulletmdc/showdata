import time
import os
from tqdm import tqdm


def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f'Start {func.__name__}')
        output = func(*args, **kwargs)
        end = time.time()
        print(f'End {func.__name__}. Elapsed {end-start} seconds')
        return output
    return wrapper


def load_dir(input_path, level):
    content_table = []
    # 处理一级目录
    if level == 1:
        for idx, img_name in enumerate(sorted(os.listdir(input_path))):
            content = {'idx': idx+1, 'img_name': img_name +
                       ' ', 'img': f"{input_path}/{img_name}"}
            content_table.append(content)

    # 处理二级目录
    elif level == 2:
        idx = 1
        for class_dir in sorted(os.listdir(input_path)):
            if not os.path.isdir(f'{input_path}/{class_dir}'):
                continue

            for img_name in sorted(os.listdir(f"{input_path}/{class_dir}")):
                img_path = f"{input_path}/{class_dir}/{img_name}"
                content = {"idx": idx, "class": class_dir,
                           'img_name': img_name+' ', 'img': img_path}
                content_table.append(content)
                idx += 1

    return content_table


def handle_src(src, output_dir, rel_path=True):
    if rel_path:
        src = os.path.relpath(src, output_dir)
        assert '..' not in src, 'The html file must in one of the parent folder of all images.'
    else:
        return src
    return src


def generate_html_table(content_table,
                        image_width='auto',
                        image_height='auto',
                        output_path='',
                        float_precision=3,
                        max_str_len=30,
                        rel_path=True,
                        save=True,
                        title="Showdata",
                        head_div=None,
                        page_size=10):
    """Generate html table

    Args:
        content_table: 2D table.
        width: image width.
        height: image height.
        output_path: output html path.
        float_precision: Max precision of float values.
        max_str_len: Max string length.
        rel_path: Whether to use the relative path of input image and output path.
        save: Whether to save output file.
        head_div: You can append some custom info in the top of the page.
        page_size: default page size.
    """
    output_dir = os.path.split(output_path)[0]
    html = '<html>'
    html += '<head>'

    html += f"""
        <title>{title}</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <meta http-equiv="Pragma" content="no-cache" />
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta http-equiv="Expires" content="0" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <link href="https://unpkg.com/jquery-resizable-columns@0.2.3/dist/jquery.resizableColumns.css" rel="stylesheet">
        <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/4.5.3/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.1/css/all.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://unpkg.zhimg.com/bootstrap-table@1.18.0/dist/bootstrap-table.min.css">
        <link href="https://unpkg.zhimg.com/bootstrap-table@1.18.0/dist/extensions/page-jump-to/bootstrap-table-page-jump-to.min.css" rel="stylesheet">
    """

    html += '</head>'
    html += '<body>'
    if head_div:
        html += head_div
    html += f"""
        <table
            class="table"
            id="table"
            data-search="true"
            data-pagination="true"
            data-show-toggle="true"
            data-show-jump-to="true"
            data-page-size="{page_size}"
            data-page-list="[10, 25, 50, 100, all]"
            data-show-refresh="true"
            data-show-fullscreen="true"
            data-show-columns="true"
            data-show-columns-toggle-all="true"
            data-show-export="true"
            data-click-to-select="true"
            data-minimum-count-columns="2"
            data-show-pagination-switch="true"
            data-id-field="id"
            data-show-footer="true"
            data-filter-control="true"
            data-resizable="true"
        >
    """

    html += '<thead>'
    html += '<tr>'
    heads = content_table[0].keys()

    for i, h in enumerate(heads):
        html += f'<th data-field="{h}" data-sortable=true data-filter-control="input">{h}</th>'

    html += "</tr>"
    html += "</thead>"
    html += '</table>'

    html += """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js" integrity="sha512-bLT0Qm9VnAYZDflyKcBaQ2gg0hSYNQrJ8RilYldYQ1FxQYoCLtUjuuRuZo+fjqhx/qtq/1itJ0C2ejDxltZVFg==" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://unpkg.com/jquery-resizable-columns@0.2.3/dist/jquery.resizableColumns.min.js"></script>
        <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/4.5.3/js/bootstrap.min.js"></script>
        <script src="https://unpkg.zhimg.com/bootstrap-table@1.18.0/dist/bootstrap-table.min.js"></script>
        <script src="https://unpkg.zhimg.com/bootstrap-table@1.18.0/dist/extensions/page-jump-to/bootstrap-table-page-jump-to.min.js"></script>
        <script src="https://unpkg.zhimg.com/bootstrap-table@1.18.1/dist/extensions/filter-control/bootstrap-table-filter-control.min.js"></script>
        <script src="https://unpkg.zhimg.com/bootstrap-table@1.18.1/dist/extensions/resizable/bootstrap-table-resizable.js"></script>
    """

    width = image_width
    height = image_height
    all_content_dict = []
    for content_row in tqdm(content_table, desc='Generating rows...'):
        content_dict = {}
        for i, head in enumerate(heads):
            content = 'None' if not head in content_row else content_row[head]
            subhtml = ''

            if type(content) == dict:  # 图片，支持更丰富的样式
                src = handle_src(content['src'], output_dir, rel_path)
                alt = '' if not "alt" in content else content['alt']
                title = '' if not "title" in content else content['title']
                item_width = width if not "width" in content else content['width']
                item_height = height if not "height" in content else content['height']
                text = '' if not "text" in content else content['text']
                style = '' if not "style" in content else content['style']
                if text != '':
                    subhtml += f"<div>{text}</div>"
                subhtml += f"<img src={src} alt=\"{alt}\" title=\"{title}\" height={item_height} width={item_width} style=\"{style}\">"

            # 图片
            elif type(content) == str and os.path.splitext(content)[-1].lower() in ['.jpg', '.png', '.jpeg', '.gif']:
                src = handle_src(content, output_dir, rel_path)
                subhtml += f"<img src={src} alt=\"{src}\" height={height} width={width}>"

            # 视频
            elif type(content) == str and os.path.splitext(content)[-1].lower() in ['.mp4', '.webm']:
                src = handle_src(content, output_dir, rel_path)
                subhtml += f"<video src={src} alt=\"{src}\" height={height} width={width} controls>"

            elif type(content) == float:
                subhtml = f"{content:.{float_precision}f}"

            else:
                if max_str_len > 0:
                    subhtml = f"{str(content)[:max_str_len]}"
                else:
                    subhtml = str(content)

            content_dict[head] = subhtml

        all_content_dict.append(content_dict)

    html += """
    <a href="https://github.com/silverbulletmdc/showdata">Use showdata: pip install showdata && showdata server (Give showdata a star in github!)</a>
    <script>
    var $table = $('#table')
    $(function() {
        var data = %s;     
        $table.bootstrapTable({data: data, paginationUseIntermediate: true})
    })
    </script>
    """ % str(all_content_dict)
    html += '</body></html>'
    if output_path == '':
        output_path = './index.html'
    if save:
        open(output_path, 'w').write(html)

    return html
