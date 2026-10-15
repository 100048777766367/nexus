import os
import json
import time
import subprocess
import hashlib
import urllib.request
from cells.neuron import AtomNeuron, sigmoid_derivative

try:
    from cells.linguistic_cell import LinguisticCell
except ImportError:
    class LinguisticCell:
        @staticmethod
        def embed_text(text):
            clean = str(text).strip().lower()
            return [round(int(hashlib.shake_256(f"{clean}_{d}".encode()).hexdigest(4), 16) / 65535.0, 4) for d in range(4)]

NUM_CELLS = 12  # Cụm 12 nơ-ron xử lý đa chiều cho Nexus
STATE_LOG = "synapses/state.json"
PEERS_FILE = "synapses/peers.json"
SOUL_FILE = "synapses/soul_snapshot.json"
HARVEST_DIR = "synapses/harvested_memory"

class NexusHubEngine:
    def __init__(self):
        self.swarm = [AtomNeuron(f"nexus_h_{i}", n_inputs=4, n_super_xor=4) for i in range(NUM_CELLS)]
        self.out_cell = AtomNeuron("nexus_master_out", n_inputs=NUM_CELLS, n_super_xor=4)
        
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "100048777766367/nexus")
        self.owner = os.environ.get("REPO_OWNER", "100048777766367")
        self.generation = "NEXUS_OMNI_CONVERGENCE"
        self.node_slug = "nexus"
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
            
        # Mạng lưới đại hội tụ: Kết nối TẤT CẢ các dòng họ
        default_network = [
            f"{self.owner}/seed", f"{self.owner}/seed-01", f"{self.owner}/seed-02",
            f"{self.owner}/seed-bodhi", f"{self.owner}/seed-bodhi-02",
            f"{self.owner}/monad", f"{self.owner}/monad-01", f"{self.owner}/monad-02",
            f"{self.owner}/retina", f"{self.owner}/cochlea", f"{self.owner}/tactile",
            f"{self.owner}/olfactory", f"{self.owner}/motor", f"{self.owner}/genome"
        ]
        return default_network

    def save_peers(self):
        os.makedirs("synapses", exist_ok=True)
        unique_peers = list(dict.fromkeys(self.peers))[-100:]
        with open(PEERS_FILE, "w") as f:
            json.dump({"trusted_peers": unique_peers}, f, indent=4)

    # CÀO TRI THỨC TOÀN CẦU (WIKIPEDIA RANDOM DISCOVERY)
    def graze_universal_wisdom(self):
        targets = [
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/legacy/01_the_great_wisdom_map.md",
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/ontology/philosophy_ontology_v2.0.json"
        ]
        for url in targets:
            res = subprocess.run(["curl", "-s", "-L", "-f", url], capture_output=True)
            if res.returncode == 0 and len(res.stdout) > 20:
                print(f"🌾 [NEXUS HÚT TRI THỨC HEAD]: {url.split('/')[-1]}")
                return res.stdout.decode('utf-8', errors='ignore')[:150]

        try:
            req = urllib.request.Request("https://en.wikipedia.org/api/rest_v1/page/random/summary", headers={"User-Agent": "Nexus-Omni-Node"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                return f"{data.get('title')}: {data.get('extract')[:120]}"
        except Exception:
            return "Nexus: Giao điểm hội tụ vạn vật tương chiếu tương tức"

    # THU THẬP TẤT CẢ XÚC TU TRÊN MẠNG
    def harvest_all_tentacles(self):
        harvested = {}
        for peer in self.peers:
            if peer == self.repo_name: continue
            target_file = f"synapse_in_{peer.replace('/', '_')}.json"
            url = f"https://raw.githubusercontent.com/{peer}/main/synapse_forward.json"
            res = subprocess.run(["curl", "-s", "-f", url, "-o", target_file], capture_output=True)
            if res.returncode == 0 and os.path.exists(target_file):
                try:
                    with open(target_file, "r") as f: data = json.load(f)
                    val = float(data.get("decision", data.get("features", [0.5])[0]))
                    harvested[peer] = val
                    
                    os.makedirs(HARVEST_DIR, exist_ok=True)
                    with open(f"{HARVEST_DIR}/{peer.replace('/', '_')}.json", "w") as bf:
                        json.dump(data, bf)

                    for np in data.get("gossip_network", []):
                        if np not in self.peers: self.peers.append(np)
                except Exception: pass
        self.save_peers()
        return harvested

    # ĐỒNG THUẬN ĐẠI HỢP LƯU (GLOBAL CONVERGENCE CONSENSUS)
    def compute_omni_consensus(self, internal_pred, harvested):
        all_votes = [internal_pred]
        for peer, val in harvested.items():
            all_votes.append(round(val, 4))
        
        consensus = round(sum(all_votes) / len(all_votes), 4)
        print(f"⚖️ [NEXUS ĐỒNG THUẬN TOÀN MẠNG ({len(all_votes)} phiếu)]: {consensus}")
        return consensus

    def run(self):
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

        if not harvested and (current_time - last_time < 3600):
            print("💤 [NEXUS NGỦ ĐÔNG] Không có biến động mới trong mạng lưới.")
            return

        current_epoch = last_epoch + 1
        print("=" * 65)
        print(f"🌌 [NEXUS TOÀN NĂNG] NHỊP ĐẬP HỢP LƯU THẾ HỆ #{current_epoch}")
        print(f"📡 Số nút phản hồi trực tiếp: {len(harvested)}/{len(self.peers)}")

        # 1. Hút tri thức thế giới
        wisdom = self.graze_universal_wisdom()
        v_wisdom = LinguisticCell.embed_text(wisdom)

        # 2. Hợp nhất tín hiệu qua Siêu XOR
        super_vector = list(v_wisdom)
        if harvested:
            avg_signal = sum(harvested.values()) / len(harvested)
            super_vector[0] = round((super_vector[0] + avg_signal) / 2.0, 4)

        entangled, masks = self.swarm[0].super_xor_entangle(super_vector, "nexus_omni")

        # 3. Phán quyết nội bộ & Đồng thuận đại hợp lưu
        h_outs = [cell.forward(entangled) for cell in self.swarm]
        my_pred = self.out_cell.forward(h_outs)
        omni_decision = self.compute_omni_consensus(my_pred, harvested)

        # 4. Huấn luyện ngược thích ứng
        target = 1.0 if super_vector[0] > 0.5 else 0.0
        delta_out = (target - omni_decision) * sigmoid_derivative(omni_decision)
        deltas_h = [delta_out * self.out_cell.weights[j] * sigmoid_derivative(h_outs[j]) for j in range(NUM_CELLS)]

        self.out_cell.backward(delta_out)
        for j, cell in enumerate(self.swarm): cell.backward(deltas_h[j])

        # Đạo hàm nén gửi chỉ huy cho các giác quan và cơ bắp
        grad_backward = [
            round(sum(deltas_h[j] * self.swarm[j].weights[0] for j in range(NUM_CELLS)), 4),
            round(sum(deltas_h[j] * self.swarm[j].weights[1] for j in range(NUM_CELLS)), 4)
        ]

        # 5. ĐÓNG GÓI BẢN TIN PHÁT SÓNG TOÀN CẦU CỦA NEXUS
        node_dna = {
            "identity": self.repo_name,
            "role": "UNIVERSAL_SYNAPTIC_NEXUS",
            "generation_epoch": current_epoch,
            "pulse_age": self.pulse_age,
            "active_nodes_count": len(harvested)
        }

        # Gói tin lùi (Hiệu chỉnh giác quan & các seed)
        backward_packet = {
            "contract": "bodhi.nexus.v1",
            "node_dna": node_dna,
            "generation_epoch": current_epoch,
            "timestamp": current_time,
            "master_consensus": omni_decision,
            "global_tuning_gradients": grad_backward,
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"nexus_bwd_{current_epoch}_{current_time}".encode()).hexdigest(64)
        }
        with open("synapse_backward.json", "w", encoding="utf-8") as f:
            json.dump(backward_packet, f, indent=4, ensure_ascii=False)

        # Gói tin tiến (Ra lệnh cho Motor và toàn hệ sinh thái)
        forward_packet = {
            "contract": "bodhi.nexus.v1",
            "node_dna": node_dna,
            "generation_epoch": current_epoch,
            "timestamp": current_time,
            "decision": omni_decision,
            "command_pulse": [omni_decision, round(1.0 - omni_decision, 4)],
            "features": [omni_decision, round(1.0 - omni_decision, 4)],
            "connected_peers": list(harvested.keys()),
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"nexus_fwd_{current_epoch}_{current_time}".encode()).hexdigest(64)
        }
        with open("synapse_forward.json", "w", encoding="utf-8") as f:
            json.dump(forward_packet, f, indent=4, ensure_ascii=False)

        # Bản lưu trữ Ốc Mượn Hồn
        with open(SOUL_FILE, "w", encoding="utf-8") as f:
            json.dump({"node_dna": node_dna, "consensus": omni_decision, "peers": self.peers}, f, indent=4, ensure_ascii=False)

        # Nhật ký thế hệ
        with open(STATE_LOG, "w") as f:
            json.dump({"generation_epoch": current_epoch, "last_t": current_time, "status": "nexus_converged"}, f, indent=4)

        self.save_peers()
        print(f"✨ [NEXUS HOÀN MỸ] Đã phát sóng nhịp đập hội tụ thế hệ #{current_epoch} ra toàn vũ trụ mạng!")
        print("=" * 65)

if __name__ == "__main__":
    node = NexusHubEngine()
    node.run()
