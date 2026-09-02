### Title
Webhook shop-domain identity not covered by HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via HMAC over the raw body only, but the `shop` attribute (taken from the unauthenticated `X-Shopify-Shop-Domain` header) is passed straight through to the app's webhook handler and never covered by that signature. This lets anyone who can obtain one valid `(raw_body, hmac)` pair swap the shop-domain header and have the payload processed as if it belonged to a different, victim tenant.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`Request#shop` simply reads the `shop-domain` header with no cryptographic binding to the body or the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` — i.e. it signs `@raw_body` only — and then, once the check passes, forwards `request.shop` unchanged into `WebhookMetadata` given to the app-supplied handler: [4](#0-3) [5](#0-4) 

This is the same class of bug as the external report: a value that is *acted on* (here, the tenant identity `shop`) is not among the bytes that are *cryptographically verified* (here, only `raw_body` is HMAC-signed). The identity binding that should hold is:
`shop attributed by the gem (request.shop) == shop that Shopify actually signed the payload for`
but the code only enforces `hmac(raw_body) == valid_hmac`, with no linkage to `shop`.

### Impact Explanation
Any entity that legitimately receives one authentic webhook delivery for their own shop (which every merchant/dev installing an app can obtain, entirely without special privileges) possesses a valid `(raw_body, hmac)` pair signed with the app's real secret. Because `shop-domain` is not part of the signed content, that same body+hmac pair can be replayed to the app's public webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header value. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the event came from a different shop (`request.shop`) that the attacker never had authorization to act on. Depending on what the handler does with `shop` (e.g. writing order/product data keyed by shop, triggering `app/uninstalled` cleanup, GDPR data-erasure processing, or session/token invalidation for that shop), this is a cross-tenant data-integrity/exfiltration vector — the impact category matches "cross-tenant access" in the Critical bucket.

### Likelihood Explanation
Exploitation requires only:
1. The attacker installs the target app on their own (attacker-owned) shop — a normal, unprivileged action, not a credential leak.
2. The attacker captures one legitimate webhook delivery (any topic) addressed to their shop, giving them a valid `raw_body` + `hmac-sha256` pair.
3. The attacker POSTs that same body/HMAC to the app's public webhook endpoint, substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with the victim's domain.

No secret key, access token, or privileged account is needed — only knowledge of one's own webhook traffic, which is inherent to running any app install. This is a straightforward, low-effort spoof once the pattern is understood, so likelihood is high given the trivial precondition.

### Recommendation
Include the shop domain (and ideally topic/api-version) inside the HMAC-signed content, or otherwise cryptographically bind them, e.g.:
```ruby
def to_signable_string
  "#{shop}\n#{topic}\n#{@raw_body}"
end
```
This requires coordinated changes on Shopify's signing side; alternatively, since the gem cannot change Shopify's signing scheme unilaterally, the gem should, at minimum, document/enforce that `shop` returned by `Request` is untrusted for authorization decisions, and encourage handlers to cross-check `request.shop` against an already-known/allow-listed set of installed shops before trusting it as a tenant identity. A more robust fix is to require callers to pass the expected shop (from their installed-shop registry) into `Registry.process` and reject mismatches against `request.shop`.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` (legitimate, unprivileged action).
2. Trigger any webhook topic (e.g. `products/update`) and capture the raw POST body `B` and its `X-Shopify-Hmac-Sha256` header value `H` (valid, computed by Shopify with the real app secret over `B`).
3. Send a new POST directly to the app's webhook endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: products/update
   X-Shopify-Hmac-Sha256: H
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Webhook-Id: <any>
   Body: B
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `hmac(B) == H` (verified in `hmac_validator.rb` lines 12-22, `request.rb` lines 35-38).
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed_body, ...)` even though the payload/body actually originated from `attacker-shop.myshopify.com` — demonstrating the cross-tenant identity confusion.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
