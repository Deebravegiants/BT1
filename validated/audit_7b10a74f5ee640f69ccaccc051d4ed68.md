### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by the application (passed to handlers as authoritative tenant/context data) come from unauthenticated HTTP headers that are never included in the signed payload. This breaks the identity binding `shop authenticated == shop acted upon`, allowing any holder of a genuinely-signed webhook body (obtainable for free by installing the public app on an attacker-owned store) to relabel that body as originating from an arbitrary victim shop.

### Finding Description
The webhook verification flow is: [1](#0-0) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)`, which delegates to `request.to_signable_string`: [2](#0-1) 

`to_signable_string` returns `@raw_body` alone — it does **not** include `shop`, `topic`, `webhook_id`, or `api_version`, all of which are read straight from attacker-controllable HTTP headers: [3](#0-2) 

Meanwhile `HmacValidator.validate_signature` only recomputes the HMAC over `to_signable_string` (the body) and compares it against the `hmac-sha256` header: [4](#0-3) 

The verified `shop` field is then handed to the application's webhook handler as trusted tenant context: [5](#0-4) 

Because Shopify signs webhooks with the app's single shared `client_secret` (not a per-shop secret), a genuine webhook obtained from *any* shop that installs the app — including a shop the attacker themselves controls (any public app can be freely installed by an unprivileged internet user) — is a validly-HMAC'd `(body, hmac)` pair. Since the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are outside the signed scope, the attacker can replay that same body/hmac pair against the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop's domain. The gem's `HmacValidator.validate` still returns `true` (it only checks the body), and `Registry.process` forwards `shop: <victim-domain>` to the handler as if Shopify itself vouched for that binding.

Root cause: the equality the app relies on is `hmac_signed(body) == authentic(shop, topic, body)`, but the code only proves `hmac_signed(body) == authentic(body)`. The `shop` (and `topic`/`webhook_id`) fields are acted upon by the handler but not bound by the HMAC — matching exactly the "field acted on but not covered by the HMAC" break-class.

### Impact Explanation
Any handler logic that keys off the `shop` value from `WebhookMetadata` (e.g., looking up the victim's stored session/access token, updating per-shop state, triggering privileged actions "for" that shop) can be triggered with attacker-controlled body content mislabeled as belonging to a shop the attacker does not control. This is a cross-tenant confusion vector: an app relying on this gem's webhook verification to establish which tenant a webhook belongs to receives no actual guarantee of that binding, enabling cross-tenant data injection/corruption using only a body signed for the attacker's own shop.

### Likelihood Explanation
Any user can install a public Shopify app on their own store for free and receive genuinely HMAC-signed webhooks for that store. No access token, `client_secret`, or privileged access is required — only the ability to relabel HTTP headers when POSTing to the app's public webhook endpoint, which is by design internet-reachable and unauthenticated other than via this HMAC check.

### Recommendation
Include the tenant-identifying fields (`shop`, and ideally `topic`/`webhook_id`) in the signed material that is verified, or otherwise cryptographically bind the `shop-domain` header value into `to_signable_string` so `HmacValidator` fails if it has been altered. At minimum, document that `request.shop` is unauthenticated and must not be trusted as verified tenant identity without additional application-level checks (e.g., cross-referencing against a shop already known to have a valid session).

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com`, receiving a real webhook POST with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker resends the same `B`/`H` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes HMAC over `B` only (per `to_signable_string`) and it matches `H`, so validation succeeds: [6](#0-5) 
4. `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, even though Shopify never issued a webhook for `victim-shop`: [7](#0-6)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
