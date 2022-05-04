import rahulscripts
from rahulscripts import run_command


def umi_run(
    sra_file,
    output_dir,
    threads=1,
    umi_length=10,
) -> None:
    """umi_run _summary_

    :param sra_file: _description_
    :type sra_file: _type_
    :param output_dir: _description_
    :type output_dir: _type_
    :param threads: _description_, defaults to 1
    :type threads: int, optional
    :param umi_length: _description_, defaults to 10
    :type umi_length: int, optional
    Perl Code: Umi-Grinder
    ref "https://github.com/FelixKrueger/Umi-Grinder"
    """

    try:
        command = f"perl {rahulscripts.__path__[0]}/external/fixed_adaper_barcode_detector_8bp.pl {sra_file} {output_dir}"  # {threads} {umi_length}"
        run_command(command)
        # print(command)
    except Exception as error:
        print(
            "Perl is not installed.\nVisit https://www.perl.org/get.html to download Perl."
            f"\n {error}"
        )
