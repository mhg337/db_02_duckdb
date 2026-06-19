import os
from dotenv import load_dotenv

# 환경 변수에서 DB_TYPE 읽기 (기본값: DUCKDB)
load_dotenv()
DB_TYPE = os.getenv("DB_TYPE", "DUCKDB").upper()

# =========================================================================
# DB_TYPE 환경 변수에 따른 음악 디깅 노트 실제 구현체 바인딩
# =========================================================================

if DB_TYPE == "DUCKDB":
    from .duckdb.connection import DuckDBManager as DatabaseManager
    from .duckdb.artist import DuckDBArtistRepository as AssetRepository
    from .duckdb.album import DuckDBAlbumRepository as AccountRepository
    from .duckdb.track import DuckDBTrackRepository as HoldingRepository
    from .duckdb.review import DuckDBReviewRepository as DailyPriceRepository
    from .duckdb.collection import DuckDBCollectionRepository as CollectionRepository
    from .duckdb.join import DuckDBJoinRepository as JoinRepository

elif DB_TYPE == "MYSQL":
    from .mysql.connection import MySQLManager as DatabaseManager
    from .mysql.artist import MySQLArtistRepository as AssetRepository
    from .mysql.album import MySQLAlbumRepository as AccountRepository
    from .mysql.track import MySQLTrackRepository as HoldingRepository
    from .mysql.review import MySQLReviewRepository as DailyPriceRepository
    from .mysql.collection import MySQLCollectionRepository as CollectionRepository
    from .mysql.join import MySQLJoinRepository as JoinRepository

else:
    raise ValueError(f"지원하지 않는 DB_TYPE 설정입니다: {DB_TYPE}")

# 활성화된 DB 환경 로그 출력
print(f"[INFO] Database Layer Component Initialized: {DB_TYPE}")

# 패키지 명시 노출
__all__ = [
    "DatabaseManager",
    "AssetRepository",
    "AccountRepository",
    "HoldingRepository",
    "DailyPriceRepository",
    "CollectionRepository",
    "JoinRepository",
]