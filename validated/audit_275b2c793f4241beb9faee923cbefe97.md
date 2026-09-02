### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, but the `shop` value that the handler subsequently trusts as the tenant identifier is read from an HTTP header that is never included in the signed material. An attacker who can obtain one genuinely-signed webhook payload (e.g., from their own store installed on the same app) can replay it with an arbitrary `X-Shopify-Shop-Domain` header and have it accepted as a valid, authenticated webhook for a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, independent of the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string` (the body), never against the headers: [3](#0-2) 

`Registry.process` performs this HMAC check and then immediately trusts `request.shop` as the authenticated tenant, forwarding it to the handler without any further binding to the signed payload: [4](#0-3) 

The identity binding that should hold is: `shop_value_verified_by_hmac == shop_value_used_by_handler`. Because the header carrying `shop` is excluded from `to_signable_string`, this equality is never enforced — the HMAC only proves "this body byte-sequence was signed by the app's secret for *some* request," not "this body was sent by shop X." Any request whose body was legitimately signed once (for any shop using the app) can be re-submitted with a forged `shop-domain` header pointing at a different shop, and `Registry.process` will treat it as an authentic webhook for that different shop.

### Impact Explanation
This breaks the tenant-authentication boundary the gem is supposed to provide to host applications: `WebhookMetadata#shop` is the field host apps use to look up per-merchant data, so a forged header lets an attacker inject attacker-controlled webhook bodies attributed to a victim shop's identity, corrupting per-tenant state or triggering shop-scoped side effects (e.g., data deletion/redaction handlers, order/customer processing) under a victim's identity. This matches the "cross-tenant access" Critical impact category, since the shop field — the tenant boundary — is not authenticated at all by the HMAC.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one validly HMAC-signed webhook body. This is realistic for any public app: an attacker can install the app on their own development store, trigger a webhook for a topic of interest, and capture the genuinely signed `(raw_body, hmac)` pair from Shopify (the shared `client_secret` is the same across all shops using the app, per `Context.api_secret_key`). They then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with the victim's shop domain. No access to the victim's credentials or the app's secret is needed.

### Recommendation
- **Short term:** Include the `shop` (and ideally `topic`/`webhook_id`) values in the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` to the verified payload before constructing `WebhookMetadata`.
- **Long term:** Audit all `VerifiableQuery` implementations (`AuthQuery`, `Request`) to ensure every field consumed downstream as an identity/tenant boundary is part of `to_signable_string`, not sourced independently from unauthenticated transport metadata.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, since `H = HMAC(client_secret, B)`), plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays the exact same `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and matches `H` — validation passes since the header is not part of the signed string: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed_body, ...)`, i.e., the app processes attacker-supplied content as an authenticated event for the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
