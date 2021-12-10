
下面就是Thompson sampling算法的代码。关键代码就是这一句：

choice = np.argmax(pymc.rbeta(1 + wins, 1 + trials - wins))

trials和wins都是向量，记载了每个杆子的历史拉动次数和赢的次数；

汤普森采样先给商品的信息(ctr)定义了先验分布，然后利用每次的观察结果去计算后验分布，
从每个商品的后验分布中采样生成随机数，取这些随机数中最大的进行推荐展示，依次循环。
由于每一轮汤普森采样中，都有根据分布采样随机数的过程，所以汤普森采样是个随机的过程。
为了每一轮迭代，方便先验概率与后验概率转化，可以使用共轭先验。
即先验概率根据观察结果更新后验概率时，分布形式不变，只有参数发生变化。
对于伯努利分布来说，共轭先验是Beta分布。
在后续迭代中，根据实验结果更新Beta分布的a、b参数即可。
这也就是为什么在ctr预估时贝叶斯平滑采用Beta先验分布的原因


def thompson_sampling(pred_df, video_df):
    # 利用池(预测的视频id
    use_pool = [i.replace("'", "").replace('"', "") for i in pred_df["content_id"].to_list()[0]]

    # 探索池
    video_df1 = video_df[~video_df["content_id"].isin(use_pool)] #上面没有的视频id
    print(video_df1.shape)
    explore_pool = video_df1.sample(n=1000,axis=0).reset_index()  #随机取1000个
    # 生成符合beta分布的样本
    explore_pool["beta"] = np.random.beta(explore_pool["hit"], (explore_pool["exposure"] - explore_pool["hit"]))
    explore_pool.drop("index",axis=1,inplace=True)

    # thompson sampling
    k = 0.1
    sampling_res = ["" for i in range(500)]
    random_num = np.random.random(size=500)
    for i in range(len(random_num)):
        if random_num[i] > k:
            sampling_res[i] = use_pool[0]
            use_pool.remove(sampling_res[i])
        else:
            sampling_res[i] = explore_pool["content_id"][explore_pool["beta"]==explore_pool["beta"].max()].values[0]
            explore_pool = explore_pool[~explore_pool["content_id"].isin([sampling_res[i]])]
return sampling_res


res_df = pred_df.groupby(['phone','bucket']).apply(lambda x : thompson_sampling(x, video_df)).reset_index()




#这个是使用pymc.rbeta的方法，简单。pip install pymc3
#α与β的初始值都为1

def Thompson_sampling1(trials, wins, p):

    b = pymc.rbeta(1 + wins, 1 + trials - wins)
    
    choice = np.argmax(b)
    
    trials[choice] += 1
    
    if p[choice] > random.random():
    
    wins[choice] += 1







#这个是使用np.random.beta()的方法，更快一点，和pymc.rbeta的方法结果差不多。

def Thompson_sampling2(trials, wins, p):
    
    pbeta = [0, 0, 0, 0, 0]
    
    for i in range(0, len(trials)):
    
    pbeta[i] = np.random.beta(wins[i]+1, trials[i]-wins[i]+1)
    choice = np.argmax(pbeta)
    
    trials[choice] += 1
    
    if p[choice] > random.random():
    
    wins[choice] += 1


def test1():

    p = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    trials = np.array([0, 0, 0, 0, 0])
    
    wins = np.array([0, 0, 0, 0, 0])
    
    for i in range(0, 10000):
    
        Thompson_sampling1(trials, wins, p)
        
        print(trials)
        
        print(wins)
        
        print(wins/trials)
        
        
def test2():

    p = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    trials = np.array([0, 0, 0, 0, 0])
    
    wins = np.array([0, 0, 0, 0, 0])
    
    for i in range(0, 10000):
    
        Thompson_sampling2(trials, wins, p)
        
        print(trials)
        
        print(wins)
        
        print(wins/trials)






test1()

test2()
