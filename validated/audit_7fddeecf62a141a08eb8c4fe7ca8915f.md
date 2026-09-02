### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable payload as the raw request body only, while the shop identity (`shop-domain` header), topic, webhook id and API version are read from unauthenticated HTTP headers and passed straight through to the app's webhook handler. This breaks the binding "shop that is cryptographically authenticated == shop acted on by the handler."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all derived from HTTP headers, none of which are included in the signable string: [2](#0-1) .

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the HMAC secret: [3](#0-2) .

`Registry.process` validates the HMAC of the body and then immediately constructs and dispatches `WebhookMetadata` using the unauthenticated `shop` header value: [4](#0-3) . `WebhookMetadata.shop` is a plain `String` field with no further verification: [5](#0-4) .

The identity binding that should hold is:
`shop_covered_by_HMAC == shop_acted_on_by_handler`

In this code, the left side does not exist at all — the HMAC only covers `raw_body` — so the equality trivially fails: the handler always acts on a `shop` value that was never part of the signed bytes.

**Exploit path (no secrets required):**
1. The attacker installs (or already has) the app on their *own*, legitimately-controlled shop (`attacker-shop.myshopify.com`). This is a normal, unprivileged action any merchant can perform.
2. Shopify sends a real webhook to the app's public endpoint for a mandatory/compliance topic (e.g. `customers/data_request`) or any subscribed topic, with a body `B` and a correctly computed `HMAC(secret, B)`. The attacker, as the receiving party's network client (or by simply capturing their own webhook traffic to their own endpoint, which requires no privilege beyond owning that shop), obtains the pair `(B, HMAC(secret, B))`.
3. The attacker replays this exact `(B, HMAC)` pair directly to the app's public webhook endpoint, but substitutes the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header with a victim shop's domain.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the HMAC only verifies `raw_body`, unchanged from step 2 [6](#0-5) .
5. The handler receives `WebhookMetadata` with `shop` set to the victim's domain and a validly-signed body, and performs the app's business logic (e.g. data deletion/redaction for `customers/redact`, `shop/redact`, cache invalidation, state updates) attributing the action to the victim tenant.

This is a genuine cross-tenant confusion primitive built entirely from the gem's own webhook-processing code, requiring no access to `api_secret_key`, no TLS interception, and no privileged account — only the ability to install the app once as an ordinary merchant and to send arbitrary POST requests to the app's public webhook URL.

### Impact Explanation
An attacker can make the app process a cryptographically-"valid" webhook while controlling which shop it is attributed to. Depending on the handler's logic, this enables cross-tenant actions: forcing GDPR redaction (`customers/redact`, `shop/redact`) against a victim shop's data, corrupting or resetting cached state keyed by shop, or triggering any shop-scoped side effect the app implements in its `WebhookHandler#handle`. This matches the "Critical — cross-tenant access" impact bucket, since the gem itself hands the handler an unauthenticated tenant identifier alongside a signature that does not actually vouch for that identifier.

### Likelihood Explanation
Likelihood is high: the only prerequisite is the ability to install the app on any shop (including a free/dev store the attacker fully controls) to obtain one legitimately-signed `(body, HMAC)` pair, and then POST it to the app's public, unauthenticated webhook endpoint with a forged `shop-domain` header. No secrets, tokens, or elevated privileges are needed. For mandatory compliance topics (`customers/redact`, `shop/redact`, `customers/data_request`) the body content is largely templated, making suitable bodies/topics easy to obtain and reuse against many target shops (mandatory topics are broadcast the same way to every installed app).

### Recommendation
Bind the shop identity (and topic/webhook id) into the HMAC-verified data, or otherwise authenticate them independently of headers before dispatch:
- Extend `Request#to_signable_string` (or add a separate check in `Registry.process`) to require that the `shop`, `topic`, and `webhook_id` header values are cross-checked against a value embedded in, or derivable from, the signed body (Shopify does not sign headers, so the safer fix is to require the app to look up/validate `shop` against its own stored installation records for that HMAC-body-shop pairing before invoking handlers), and reject the request if it cannot be reconciled.
- At minimum, document/enforce that `WebhookMetadata#shop` must never be trusted for authorization decisions without an independent verification step, and add a code path in `Registry.process` that fails closed when the header-derived shop cannot be corroborated.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the app normally.
# Shopify sends a legitimate webhook to the app for that shop:
body = '{"id":123,"redact":true}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), real_api_secret_key, body)

# Attacker replays the same (body, hmac) but swaps the shop-domain header:
forged_headers = {
  "shopify-topic"        => "customers/redact",
  "shopify-hmac-sha256"  => Base64.encode64(hmac),
  "shopify-shop-domain"  => "victim-shop.myshopify.com", # <-- forged, not covered by HMAC
  "shopify-webhook-id"   => "any-id",
  "shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) succeeds (only body is checked),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)) is invoked.
```
`Registry.process` source confirming the validation-then-dispatch flow: [4](#0-3) ; `Request` header parsing confirming `shop` is never part of the signed bytes: [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
