from abc import ABC, abstractmethod
import pandas as pd

# =========================================================================
# [조건 충족 1] 데이터베이스 연결 및 자원 관리 인터페이스
# =========================================================================
class IDatabaseManager(ABC):
    """DuckDB / MySQL 등 물리 DB 커넥션을 획득하고 해제하는 인터페이스"""

    @abstractmethod
    def get_connection(self):
        """데이터베이스 커넥션 객체 반환 (DuckDB Connection 등)"""
        ...

    @abstractmethod
    def close(self) -> None:
        """활성화된 데이터베이스 커넥션 자원 반환"""
        ...


# =========================================================================
# [조건 충족 2] 공통 레포지토리 추상 인터페이스 (기본 메타 연산 규격 강제)
# =========================================================================
class IRepository(ABC):
    """모든 도메인 테이블 레포지토리의 기반이 되는 공통 추상 클래스"""
    
    def __init__(self, db: IDatabaseManager):
        # 생성자를 통해 상위 레이어에서 관리되는 커넥션을 주입(DI)받음
        self._con = db.get_connection()

    @abstractmethod
    def create_table(self) -> None:
        """최초 구동 시 DuckDB 내에 해당 도메인 테이블을 생성하는 DDL 실행"""
        ...

    @abstractmethod
    def count(self) -> int:
        """테이블의 Cardinality(총 행의 개수)를 연산하여 반환"""
        ...


# =========================================================================
# [조건 충족 3] 각 테이블별 CRUD 확장 인터페이스 설계
# =========================================================================

class IArtistRepository(IRepository):
    """Artists (아티스트) 테이블 접근 인터페이스"""

    @abstractmethod
    def save(self, df: pd.DataFrame) -> None:
        """아티스트 신규 등록 및 수정을 DataFrame 단위로 수용하여 반영 (Create/Update)"""
        ...

    @abstractmethod
    def find_all(self) -> pd.DataFrame:
        """전체 아티스트 목록을 조회하여 Flet UI로 전달 (Read)"""
        ...


class IAlbumRepository(IRepository):
    """Albums (앨범) 테이블 접근 인터페이스"""

    @abstractmethod
    def save(self, df: pd.DataFrame) -> None:
        """앨범 마스터 데이터의 등록 및 정보 갱신을 수행 (Create/Update)"""
        ...

    @abstractmethod
    def find_by_id(self, album_id: int) -> pd.DataFrame:
        """Flet 상세 페이지 구동을 위해 특정 앨범 데이터를 단건 조회 (Read)"""
        ...


class ITrackRepository(IRepository):
    """Tracks (수록곡) 테이블 접근 인터페이스"""

    @abstractmethod
    def save(self, df: pd.DataFrame) -> None:
        """앨범별 수록곡 리스트 데이터를 적재 (Create)"""
        ...

    @abstractmethod
    def find_by_album_id(self, album_id: int) -> pd.DataFrame:
        """[Use Case 3.1.2 대응] 특정 앨범의 수록곡들을 트랙 번호순으로 정렬하여 조회 (Read)"""
        ...


class IReviewRepository(IRepository):
    """Reviews (유저 평점 및 한줄평) 테이블 접근 인터페이스"""

    @abstractmethod
    def save(self, df: pd.DataFrame) -> None:
        """[Use Case 3.2 대응] 유저가 Flet 입력 필드에 작성한 리뷰 행 데이터를 DuckDB에 삽입 (Create)"""
        ...

    @abstractmethod
    def delete_by_id(self, review_id: int) -> None:
        """리뷰 ID를 지정하여 작성한 데이터를 원자적 삭제 (Delete)"""
        ...


class ICollectionRepository(IRepository):
    """Collections 및 Collection_Albums (테마 보관함) 통합 제어 인터페이스"""

    @abstractmethod
    def save_collection(self, df: pd.DataFrame) -> None:
        """[Use Case 3.4 대응] 새로운 테마 보관함 마스터 정보를 생성 (Create)"""
        ...

    @abstractmethod
    def save_collection_album(self, df: pd.DataFrame) -> None:
        """[Use Case 3.4 대응] 특정 컬렉션 내부에 사용자가 선택한 앨범 매핑 관계를 추가 (Create)"""
        ...


# =========================================================================
# [조건 충족 4] 다중 테이블 Join 연산 전용 독립 인터페이스 (1개 설계 완료)
# =========================================================================
class IJoinRepository(ABC):
    """복잡한 비즈니스 화면 출력을 처리하기 위한 다중 테이블 Join 전용 인터페이스"""

    def __init__(self, db: IDatabaseManager):
        self.con = db.get_connection()

    @abstractmethod
    def find_artists_with_albums(self, keyword: str = None) -> pd.DataFrame:
        """
        [Use Case 3.1 대응 복합 조인]
        사용자가 Flet 검색창에 입력한 키워드를 바탕으로 아티스트 정보와 앨범 타이틀, 
        발매년도, 이미지 경로를 연쇄 LEFT JOIN하여 단일 DataFrame으로 결합 반환합니다.
        """
        ...

    @abstractmethod
    def find_integrated_reviews(self, album_id: int) -> pd.DataFrame:
        """
        [Use Case 3.3 대응 복합 조인]
        앨범 상세 화면 하단에 노출할 평점 피드를 빌드하기 위해, Reviews 테이블과 Users 테이블을 
        내부 조인(JOIN)하여 유저 닉네임, 별점, 코멘트 텍스트, 생성 날짜를 일괄 반환합니다.
        """
        ...