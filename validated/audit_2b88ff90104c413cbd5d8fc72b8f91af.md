### Title
Webhook HMAC Validation Does Not Bind the `shop-domain` Header, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes an incoming webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value taken from an HTTP header that is never included in that HMAC computation. Because a given app's webhook signing secret (`Context.api_secret_key`) is identical across every merchant/shop that has the app installed, any merchant can capture (or trivially reproduce, e.g. via their own store's real webhook deliveries) a valid `(body, hmac)` pair and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop, causing the handler to process attacker-supplied data under the victim's tenant identity.

### Finding Description
The identity binding that should hold is:

`hmac_verified_bytes == bytes_used_to_determine_tenant(shop)`

but in this gem it is:

`hmac_verified_bytes == raw_body` while `shop = header["shopify-shop-domain"]` (unauthenticated)

Evidence:
- `Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 
- `Webhooks::Request#shop` reads the shop identity straight from a header, with no cross-check against anything covered by the signature: [2](#0-1) 
- `HmacValidator.validate` / `validate_signature` compute and compare the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the body), never over the shop/topic/webhook-id headers: [3](#0-2) 
- `Registry.process` gates entirely on this body-only HMAC check and then forwards the unauthenticated `request.shop` straight to the app's handler as the tenant identity: [4](#0-3) 

Since Shopify signs webhook bodies with the app's single `client_secret` (shared across all shops that install the app), an attacker who is simply a normal merchant with the app installed can trigger a real webhook to the app's public callback URL (e.g., by placing an order), which yields a body/HMAC pair valid for the app-wide secret. The gem gives that attacker no mechanism to detect the header/body mismatch; it only checks HMAC(body). The attacker can then resend the identical `(body, hmac)` to the same endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header overwritten to a victim shop's domain, and `HmacValidator.validate` still returns `true`, so `Registry.process` will happily dispatch it to the topic handler labeled as coming from the victim shop.

### Impact Explanation
This breaks the tenant/shop identity boundary the HMAC is supposed to enforce: an app handler that trusts `WebhookMetadata#shop` (as the gem's own webhook infrastructure encourages, since it's the only value exposed for tenant lookup) can be made to write, delete, or process data as if it originated from an arbitrary victim shop — a cross-tenant access/data-injection primitive achievable by any unprivileged app-installer, without needing the app's `client_secret`, an access token, or any credential belonging to the victim. This matches the "Critical — cross-tenant access" impact category.

### Likelihood Explanation
High. No secrets or privileged access are required — only that the attacker install the app on any shop they control (or otherwise obtain one legitimate signed webhook delivery) and can send arbitrary HTTP requests (with arbitrary headers) to the app's public webhook callback URL, which is inherently internet-reachable.

### Recommendation
Bind the shop (and ideally topic/webhook-id/api-version) into the value that is HMAC-verified, or otherwise independently authenticate the shop header before trusting it — e.g., by including it in `to_signable_string`, or by requiring the caller to cross-check `request.shop` against a shop known to be authorized/installed via a source verified independently of these headers, before it's passed to `WebhookMetadata`.

### Proof of Concept
1. App installs webhook `orders/create` pointing at `https://app.example.com/webhooks`.
2. Attacker (a normal merchant `attacker-shop.myshopify.com` with the app installed) places an order, causing Shopify to POST to the endpoint with body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(client_secret, B)`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` (e.g., replays through their own logging proxy in front of the webhook endpoint, or via any request interception they control since it's their own traffic).
4. Attacker sends a new HTTP request directly to `https://app.example.com/webhooks` with the same body `B` and `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this, `Utils::HmacValidator.validate` succeeds (it only checks `B`/`H`), and `Registry.process` invokes the topic handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled body `B`, corrupting/injecting data attributed to the victim tenant. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
