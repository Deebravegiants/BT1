I have enough evidence to confirm the vulnerability.

### Title
Webhook `shop` domain is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the raw `X-Shopify-Shop-Domain` header, but `Utils::HmacValidator` only verifies the HMAC over the request body. The `shop` (and `topic`/`webhook_id`/`api_version`) values used by `Registry.process` to build `WebhookMetadata` and dispatch to the app's handler are never covered by the cryptographic signature, breaking the binding `authenticated_shop == attributed_shop`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header with no relation to the signed content: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC only over `to_signable_string` (i.e. the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` gates purely on that body HMAC, then trusts `request.shop` (and `request.topic`) verbatim when building the `WebhookMetadata` passed to the app's registered handler: [4](#0-3) 

`WebhookMetadata.shop` is the field host apps use to attribute the event to a specific merchant/tenant, per the gem's own documentation: [5](#0-4) 

Root cause: the identity binding the gem is supposed to enforce is `hmac_verified(body) ∧ shop_header == shop_that_produced(body)`. Instead it only enforces `hmac_verified(body)`; `shop_header` is accepted independent of the signature. Because the app's HMAC secret (`Context.api_secret_key`) is shared across every shop that installs the app, a valid `(body, hmac)` pair generated for one tenant remains valid for any `shop-domain` value an attacker chooses to attach to it — the header is never part of the signed bytes.

### Impact Explanation
An unprivileged internet user who has installed (or can install) the app on their own shop can capture a legitimate webhook Shopify sends them (valid `raw_body` + valid `hmac-sha256` for that body, signed with the app's real secret), then replay that exact HTTP request to the app's public webhook endpoint while only changing the `X-Shopify-Shop-Domain` header to name a victim shop that also has the app installed. `HmacValidator.validate` still returns `true` (it never looked at the header), so `Registry.process` dispatches `WebhookMetadata` with `shop` set to the victim's domain. Any host app that uses `data.shop` (as the gem's own docs instruct) to look up the victim's stored session/access token and act on their store — write orders/metafields, process refunds, mark GDPR redaction requests, etc. — will now execute those actions attributed to and scoped to the victim tenant, using the victim's credentials, based entirely on attacker-supplied, unauthenticated header content. This is a cross-tenant confusion / cross-tenant access vulnerability crossing the app's per-shop authentication boundary.

### Likelihood Explanation
High. No secret material is required — only participation as a normal merchant/user who can install the app on a shop they control and capture one webhook delivery to their own endpoint, then replay it with a modified header. The webhook endpoint is public-facing by design (Shopify calls it over the internet), and nothing in `Request` or `Registry` cross-checks `shop` against the signed payload.

### Recommendation
Include the tenant-identifying header (`shop-domain`, and ideally `topic`/`webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before trusting `request.shop` in `Registry.process`. At minimum, `Request#to_signable_string` should incorporate these header values so `HmacValidator.validate` fails when they are altered independently of the body, or the registry should independently verify that the shop asserted in the webhook matches a shop actually subscribed to that specific `webhook_id`/topic before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) delivered to the app's public endpoint. They capture the raw HTTP request: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's shared `client_secret`), and header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical body `B` and header `H` to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. Server calls `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` then `Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)` and compares to `H` — it matches (body unchanged), so validation passes: [6](#0-5) 
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)` and invokes the host app's handler, which acts on `victim-shop.myshopify.com` using data/credentials belonging to the victim tenant, even though the payload actually originated from the attacker's own shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
