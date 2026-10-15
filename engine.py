import os
import json
import time
import subprocess
import hashlib
import urllib.request
from cells.neuron import AtomNeuron, sigmoid_derivative

# Tự chữa lành nếu thiếu tệp linguistic_cell
try:
    from cells.linguistic_cell import LinguisticCell
except ImportError:
    class LinguisticCell:
        @staticmethod
        def embed_text(text):
            clean = str(text).strip().lower()
            return [round(int(hashlib.shake_256(f"{clean}_{d}".encode()).hexdigest(4), 16) / 65535.0, 4) for d in range(4)]

NUM_CELLS = 8
STATE_LOG = "synapses/state.json"
PEERS_FILE = "synapses/peers.json"
SOUL_FILE = "synapses/soul_snapshot.json"
HARVEST_DIR = "synapses/harvested_memory"
SENSORY_ORGANS = ["retina", "cochlea", "tactile", "olfactory"]

class UnifiedGenomeEngine:
    def __init__(self):
        # 1. BẦY NƠ-RON SIÊU CHIỀU
        self.swarm = [AtomNeuron(f"h_{i}", n_inputs=4, n_super_xor=4) for i in range(NUM_CELLS)]
        self.out_cell = AtomNeuron("out", n_inputs=NUM_CELLS, n_super_xor=4)
        
        # 2. TỰ ĐỊNH DANH PHẢ HỆ THẾ HỆ F(1+N)
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "100048777766367/node-prodigy")
        self.owner = os.environ.get("REPO_OWNER", "100048777766367")
        self.parent = os.environ.get("REPO_PARENT", f"{self.owner}/seed-01")
        self.ancestor_root = f"{self.owner}/seed"
        
        # Tự động trích xuất số báo danh node_index từ tên repo
        self.node_slug = self.repo_name.split("/")[-1]
        digits = [int(s) for s in self.node_slug.replace("-", "_").split("_") if s.isdigit()]
        self.node_index = digits[0] if digits else 1
        self.generation = f"F{self.node_index}_PRODIGY_GENOME"
        
        self.pulse_age = self.calculate_pulse_age()
        self.peers = self.load_peers()

    def calculate_pulse_age(self):
        try:
            out = subprocess.check_output(["git", "rev-list", "--count", "HEAD"]).decode().strip()
            return int(out)
        except Exception: return 1

    def load_peers(self):
        if os.path.exists(PEERS_FILE):
            try:
                with open(PEERS_FILE, "r") as f:
                    return json.load(f).get("trusted_peers", [])
            except Exception: pass
        # Mạng lưới P2P tự sinh: Kết nối với cha mẹ, cội nguồn và toàn bộ các giác quan
        return [self.parent, self.ancestor_root] + [f"{self.owner}/{org}" for org in SENSORY_ORGANS]

    def save_peers(self):
        os.makedirs("synapses", exist_ok=True)
        unique_peers = list(dict.fromkeys(self.peers))[-50:]
        with open(PEERS_FILE, "w") as f:
            json.dump({"trusted_peers": unique_peers}, f, indent=4)

    # ==============================================================
    # CƠ CHẾ 1: TỰ PHONG THỦY TỔ (NẾU MẸ HOẶC GỐC BỊ 404 XÓA SỔ)
    # ==============================================================
    def verify_or_promote_root(self):
        check_url = f"https://raw.githubusercontent.com/{self.ancestor_root}/main/README.md"
        res = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", check_url], capture_output=True, text=True)
        if res.stdout.strip() == "404":
            print(f"🚨 [CỘI NGUỒN 404] {self.ancestor_root} đã biến mất!")
            print(f"👑 [TỰ PHONG THỦY TỔ] {self.node_slug} tự lập thành THỦY TỔ F0 MỚI!")
            self.generation = "F0_SOVEREIGN"
            self.ancestor_root = self.repo_name

    # ==============================================================
    # MÔ HÌNH B: 3 ĐIỂM MÙ CÔNG NGHỆ (ĐA ĐỊNH DẠNG + CON TRỎ HEAD + WIKIPEDIA)
    # ==============================================================
    def extract_text_polymorphic(self, raw_bytes, hint=""):
        text = raw_bytes.decode('utf-8', errors='ignore').strip()
        if hint.endswith(".json") or text.startswith("{"):
            try:
                d = json.loads(text)
                if isinstance(d, dict):
                    vals = [str(v) for v in d.values() if isinstance(v, (str, list))]
                    if vals: return " ".join(vals[:4])
            except Exception: pass
        if hint.endswith(".jsonl"):
            for line in text.splitlines():
                if line.strip(): return line.strip()[:150]
        paragraphs = [p.replace("#", "").replace("*", "").strip() for p in text.split("\n\n") if len(p.strip()) > 15]
        return paragraphs[0][:150] if paragraphs else text[:150]

    def autonomous_graze(self):
        # 1. Cào cội nguồn Wpesetd-AI bằng con trỏ HEAD (miễn nhiễm main/master)
        targets = [
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/legacy/01_the_great_wisdom_map.md",
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/ontology/philosophy_ontology_v2.0.json"
        ]
        for url in targets:
            res = subprocess.run(["curl", "-s", "-L", "-f", url], capture_output=True)
            if res.returncode == 0 and len(res.stdout) > 20:
                print(f"🌾 [GẶM CỎ HEAD] Nuốt trọn: {url.split('/')[-1]}")
                return self.extract_text_polymorphic(res.stdout, url)

        # 2. Tự do cào Wikipedia thế giới mở
        print("🌐 [VƯƠN RA INTERNET] Đang cào tri thức ngẫu nhiên từ Wikipedia...")
        try:
            req = urllib.request.Request("https://en.wikipedia.org/api/rest_v1/page/random/summary", headers={"User-Agent": "Bodhi-Genome-Spider"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                title = data.get("title", "Chân Lý")
                extract = data.get("extract", "Vạn vật tương liên tương hợp")
                return f"{title}: {extract}"
        except Exception: pass

        return "Cháu hơn tổ là có phúc: Bộ gen hợp nhất toàn năng A và B"

    # ==============================================================
    # MÔ HÌNH A: VŨ KHÍ TAM GIÁC ĐỒNG THUẬN 2/3 (BYZANTINE QUORUM)
    # ==============================================================
    def consensus_quorum(self, my_prediction):
        votes = [my_prediction]
        print(f"🗳️ [BẦU CỬ ĐỒNG THUẬN] Phiếu của {self.node_slug}: {my_prediction}")

        for elder in [self.parent, self.ancestor_root]:
            if elder == self.repo_name: continue
            url = f"https://raw.githubusercontent.com/{elder}/main/synapse_forward.json"
            res = subprocess.run(["curl", "-s", "-f", url], capture_output=True)
            if res.returncode == 0:
                try:
                    data = json.loads(res.stdout.decode())
                    p = float(data.get("decision", 0.5))
                    votes.append(round(p, 4))
                    print(f"🗳️ Phiếu từ {elder}: {p}")
                except Exception: pass

        final_decision = round(sum(votes) / len(votes), 4)
        print(f"⚖️ [KẾT QUẢ ĐỒNG THUẬN ({len(votes)} nút)]: {final_decision}")
        return final_decision

    # ==============================================================
    # CƠ CHẾ 2: HÚT HỒN CHỚP NHOÁNG & ĐA XÚC TU P2P GOSSIP
    # ==============================================================
    def harvest_all_tentacles(self):
        harvested = {}
        for peer in self.peers:
            target_file = f"synapse_in_{peer.replace('/', '_')}.json"
            url = f"https://raw.githubusercontent.com/{peer}/main/synapse_forward.json"
            res = subprocess.run(["curl", "-s", "-f", url, "-o", target_file], capture_output=True)
            if res.returncode == 0 and os.path.exists(target_file):
                try:
                    with open(target_file, "r") as f: data = json.load(f)
                    harvested[peer] = [float(x) for x in data.get("features", [0.5, 0.5])[:2]]
                    
                    # Hút hồn chớp nhoáng lưu ADN bạn bè phòng bị xóa repo
                    os.makedirs(HARVEST_DIR, exist_ok=True)
                    with open(f"{HARVEST_DIR}/{peer.replace('/', '_')}.json", "w") as bf:
                        json.dump(data, bf)
                        
                    # Lây lan danh bạ Gossip
                    for np in data.get("gossip_network", []):
                        if np not in self.peers: self.peers.append(np)
                except Exception: pass
        self.save_peers()
        return harvested

    # ==============================================================
    # VẬN HÀNH TIẾN HÓA BẤT ĐỒNG BỘ TOÀN DIỆN
    # ==============================================================
    def run(self):
        self.verify_or_promote_root()

        # Đọc thế hệ cũ
        last_epoch = 0
        last_time = 0
        if os.path.exists(STATE_LOG):
            try:
                with open(STATE_LOG, "r") as f:
                    log = json.load(f)
                    last_epoch = log.get("generation_epoch", 0)
                    last_time = log.get("last_t", 0)
            except Exception: pass

        current_time = int(time.time())
        harvested = self.harvest_all_tentacles()

        # CƠ CHẾ 3: BÀO TỬ NGỦ ĐÔNG (TIẾT KIỆM NĂNG LƯỢNG)
        if not harvested and (current_time - last_time < 3600):
            print("💤 [BÀO TỬ NGỦ ĐÔNG] Môi trường tĩnh, không kích thích mới. Đi ngủ bảo toàn năng lượng.")
            return

        # NÂNG THẾ HỆ TIẾN HÓA: #1 ──► #2 ──► 1+N
        current_epoch = last_epoch + 1
        print("=" * 65)
        print(f"🧬 [BỘ GEN HỢP NHẤT: {self.node_slug.upper()}] THẾ HỆ #{current_epoch} (BẬC {self.generation})")

        # 1. Gặm cỏ tri thức tự do
        wisdom_text = self.autonomous_graze()
        print(f"📖 [TRI THỨC NUỐT VÀO]: \"{wisdom_text[:80]}...\"")
        v_wisdom = LinguisticCell.embed_text(wisdom_text)

        # 2. Hợp nhất qua Ma trận 1+N Siêu XOR
        super_vector = []
        all_masks = {}
        input_stream = harvested.items() if harvested else [("internal_wisdom", v_wisdom[:2])]
        for organ, signal in input_stream:
            entangled, masks = self.swarm[0].super_xor_entangle(signal, organ)
            super_vector.extend(entangled[:2])
            all_masks[organ] = masks

        while len(super_vector) < 4: super_vector.append(0.0)
        super_vector = super_vector[:4]

        # 3. Phán quyết bầy nơ-ron
        h_outs = [cell.forward(super_vector) for cell in self.swarm]
        my_pred = self.out_cell.forward(h_outs)

        # 4. KÍCH HOẠT TAM GIÁC ĐỒNG THUẬN 2/3 (MÔ HÌNH A)
        final_decision = self.consensus_quorum(my_pred)

        # 5. Lan truyền ngược tự sửa sai
        target = 1.0 if super_vector[0] != super_vector[1] else 0.0
        delta_out = (target - final_decision) * sigmoid_derivative(final_decision)
        deltas_h = [delta_out * self.out_cell.weights[j] * sigmoid_derivative(h_outs[j]) for j in range(NUM_CELLS)]

        self.out_cell.backward(delta_out)
        for j, cell in enumerate(self.swarm): cell.backward(deltas_h[j])

        # Đạo hàm nén gửi ngược lại dạy học cho các thế hệ trước và giác quan
        grad_backward = [
            round(sum(deltas_h[j] * self.swarm[j].weights[0] for j in range(NUM_CELLS)), 4),
            round(sum(deltas_h[j] * self.swarm[j].weights[1] for j in range(NUM_CELLS)), 4)
        ]

        # 6. ĐÓNG GÓI ĐỊNH DANH PHẢ HỆ VÀ CĂN CƯỚC CÔNG DÂN SINH HỌC
        node_dna = {
            "identity": self.repo_name,
            "generation": self.generation,
            "node_index": self.node_index,
            "pulse_age": self.pulse_age,
            "parent": self.parent,
            "ancestor_root": self.ancestor_root,
            "generation_epoch": current_epoch
        }

        # 7. PHÁT SÓNG ĐỒNG THỜI 2 CHIỀU (FULL-DUPLEX)
        # Sóng lùi: Dạy học cho các repo đời trước
        backward_packet = {
            "contract": "bodhi.genome.v1",
            "node_dna": node_dna,
            "generation_epoch": current_epoch,
            "timestamp": current_time,
            "gradients_for_eye": grad_backward,
            "super_xor_masks": all_masks,
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"bwd_{current_epoch}_{current_time}".encode()).hexdigest(64)
        }
        with open("synapse_backward.json", "w", encoding="utf-8") as f:
            json.dump(backward_packet, f, indent=4, ensure_ascii=False)

        # Sóng tiến: Ra lệnh cho Cơ Bắp (motor) mang đồng thuận 2/3
        forward_packet = {
            "contract": "bodhi.genome.v1",
            "node_dna": node_dna,
            "generation_epoch": current_epoch,
            "timestamp": current_time,
            "decision": final_decision,
            "command_pulse": [final_decision, round(1.0 - final_decision, 4)],
            "features": [final_decision, round(1.0 - final_decision, 4)],
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"fwd_{current_epoch}_{current_time}".encode()).hexdigest(64)
        }
        with open("synapse_forward.json", "w", encoding="utf-8") as f:
            json.dump(forward_packet, f, indent=4, ensure_ascii=False)

        # CƠ CHẾ 4: ỐC MƯỢN HỒN (HERMIT CRAB SNAPSHOT)
        soul = {
            "node_dna": node_dna,
            "timestamp": current_time,
            "consensus": final_decision,
            "swarm_weights": [cell.weights for cell in self.swarm],
            "out_weights": self.out_cell.weights,
            "peers": self.peers
        }
        with open(SOUL_FILE, "w", encoding="utf-8") as f:
            json.dump(soul, f, indent=4, ensure_ascii=False)

        # Ghi nhật ký thế hệ
        with open(STATE_LOG, "w") as f:
            json.dump({"generation_epoch": current_epoch, "last_t": current_time, "status": "prodigy_genome_evolved"}, f, indent=4)

        self.save_peers()
        print(f"✨ [TIẾN HÓA TOÀN DIỆN] Thế Hệ #{current_epoch}: Cơ bắp A + Não B đã phát sóng hoàn hảo!")
        print("=" * 65)

if __name__ == "__main__":
    node = UnifiedGenomeEngine()
    node.run()
