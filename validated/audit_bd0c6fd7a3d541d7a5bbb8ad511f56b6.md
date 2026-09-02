### Title
`Webhooks::Registry.process` trusts the unauthenticated `shop`/`topic` headers even though only the raw body is covered by the HMAC — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by checking the HMAC over the *raw body only*, but then dispatches and hands the handler the *shop domain* and *topic* read from **unauthenticated HTTP headers**. The identity binding "shop the data is attributed to" == "shop that was cryptographically verified" is broken, exactly mirroring the reported bug class (checking one value while acting on a different, unverified one).

### Finding Description
`Utils::HmacValidator.validate` only signs/verifies `verifiable_query.to_signable_string`, and for webhooks that string is defined as the raw body: [1](#0-0) 

None of `topic`, `shop`, `webhook_id`, or `api_version` are included in the signed payload — they are read straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC of the body, then uses the unauthenticated `request.topic` to pick a handler, and forwards the unauthenticated `request.shop` (and `request.topic`) to that handler as the trusted identity of the event: [4](#0-3) 

So the equality actually enforced is:
`HMAC(secret, raw_body) == received_hmac`

while the equality the application relies on (per the gem's documented contract, `WebhookMetadata#shop`/`#topic`) is:
`shop_header == "shop the body actually originated from"`

These are not the same guarantee. Any request whose `raw_body` + `hmac-sha256` pair is genuine (i.e., produced by Shopify for *some* real webhook delivery) will pass validation regardless of what `shop-domain`/`topic` headers are attached, because those headers are never hashed.

### Impact Explanation
A merchant who installs the app on their own store (an "unprivileged" tenant relative to other merchants of the same app) can trigger arbitrary genuine webhook deliveries with content they fully control (e.g., create a customer/order with attacker-chosen fields) and thereby obtain a legitimate `(raw_body, hmac)` pair signed with the app's shared `api_secret_key`. Because `shop-domain` and `topic` are not covered by that signature, the attacker can replay the exact same body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop and/or the `X-Shopify-Topic` header for a different registered topic. `Registry.process` will accept it as authentic and hand the host application a `WebhookMetadata` claiming the (attacker-crafted) data belongs to the victim shop / to a different event type. This is a cross-tenant identity-spoofing primitive (e.g. can be used to make the app believe an `app/uninstalled` or `customers/redact` event, or attacker-controlled order/customer data, came from a victim shop), satisfying the "cross-tenant access" Critical impact category, using only the gem's own documented `Webhooks::Registry.process` / `Webhooks::Request` API.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the target app on a shop the attacker controls (a normal, low-privilege action any Shopify merchant can take for public apps), and (2) the ability to POST directly to the app's public webhook endpoint with custom headers, which is trivial for any internet client since the endpoint is unauthenticated by design (HMAC is the only check). No access token, client secret, or TLS interception is needed.

### Recommendation
Bind the identity fields to the signature: include `shop-domain`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed payload (e.g., sign `headers + body` or a canonical concatenation of them) instead of the raw body alone, and reject requests whose header-derived shop/topic don't match the payload actually intended by Shopify. At minimum, `Webhooks::Request#to_signable_string` should incorporate the header values that `Registry.process` subsequently trusts.

### Proof of Concept
1. App is installed on attacker's own shop `attacker.myshopify.com`. Attacker creates a customer/order with attacker-chosen field values, causing Shopify to deliver a genuine webhook to the app's endpoint with a valid `X-Shopify-Hmac-Sha256` for that `raw_body`.
2. Attacker captures `raw_body` and its `hmac-sha256` value (e.g., via a proxy under their control, or by having their own webhook endpoint mirror to the app).
3. Attacker POSTs the identical `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: <any topic registered by the app>`
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) validates the HMAC (passes, since body unchanged), looks up the handler for the spoofed topic, and calls `handler.handle` with `shop: "victim-shop.myshopify.com"` — data now falsely attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
