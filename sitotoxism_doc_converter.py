from langchain.schema import Document

def create_document_from_data(source : str, rows : list) -> list:

    sitotoxism_docs = []

    for row in rows:

        if source == "region":

            id = f"{row.get('OCCRNC_YEAR')}-{row.get('OCCRNC_MM')}-{row.get('OCCRNC_AREA')}"

            content = (
                f"{row.get('OCCRNC_YEAR', '?')}년 {row.get('OCCRNC_MM', '?')}월, "
                f"{row.get('OCCRNC_AREA', '?')} 지역에서 식중독이 {row.get('OCCRNC_CNT', '?')}건 발생했으며 "
                f"환자 수는 {row.get('PATNT_CNT', '?')}명이었습니다."
            )

        elif source == "facility":

            id = f"{row.get('OCCRNC_YEAR')}-{row.get('OCCRNC_MM')}-{row.get('OCCRNC_PLC')}"

            content = (
                f"{row.get('OCCRNC_YEAR', '?')}년 {row.get('OCCRNC_MM', '?')}월, "
                f"{row.get('OCCRNC_PLC', '?')} 시설에서 식중독이 {row.get('OCCRNC_CNT', '?')}건 발생했으며 "
                f"환자 수는 {row.get('PATNT_CNT', '?')}명이었습니다."
            )

        elif source == "virus":

            id = f"{row.get('OCCRNC_YEAR')}-{row.get('OCCRNC_MM')}-{row.get('OCCRNC_VIRS')}"

            content = (
                f"{row.get('OCCRNC_YEAR', '?')}년 {row.get('OCCRNC_MM', '?')}월, "
                f"{row.get('OCCRNC_VIRS', '?')} 물질로 인해 식중독이 {row.get('OCCRNC_CNT', '?')}건 발생했고 "
                f"환자 수는 {row.get('PATNT_CNT', '?')}명이었습니다."
            )

        else:
            id = "unknown"
            content = str(row)

        doc = Document(page_content = content, metadata = {"source" : source, "sitotoxism_id" : id})
        
        sitotoxism_docs.append(doc)

    return sitotoxism_docs