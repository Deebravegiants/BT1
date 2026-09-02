Based on my investigation, I found a genuine, in-scope vulnerability that matches the exact bug-class hint in the rules ("a field acted on but not covered by the HMAC").

### Title
Webhook shop/topic/webhook_id/api_version fields are trusted for tenant attribution despite being excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop, topic, webhook_id and api_version fields used to route and attribute the webhook are all read from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` authenticates a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the caller-supplied `hmac` field with `OpenSSL.secure_compare` [1](#0-0) . For webhook requests, `Request#to_signable_string` returns only `@raw_body` [2](#0-1) , meaning the HMAC covers nothing but the JSON body bytes.

However, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) which are never included in the signable string [3](#0-2) . `Registry.process` validates only the HMAC (i.e., only the body) and then builds `WebhookMetadata` directly from these unauthenticated header values, passing them straight to the app-provided handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [4](#0-3) .

The identity binding broken here is: **shop (and topic/webhook_id) acted upon by the handler == shop (and topic/webhook_id) covered by the HMAC**. In fact: `shop_acted_on ⊄ HMAC-covered bytes`. Because the app's `api_secret_key` (the webhook signing secret) is shared across all shops that install the app — not per-tenant — anyone who operates their own shop with the app installed can capture one legitimately Shopify-signed webhook body+HMAC pair, then replay that exact `raw_body`/`hmac-sha256` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers with values belonging to a different (victim) tenant. `HmacValidator.validate` still succeeds because it never inspected those headers, and the app's `WebhookHandler.handle` receives `WebhookMetadata` falsely attributing the (attacker-controlled/replayed) event to the victim shop [5](#0-4) . Any host app that keys off `data.shop` to look up per-tenant state, enqueue jobs, or make further authenticated API calls on the app's behalf — exactly as the gem's own documented example does (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [6](#0-5)  — will process cross-tenant data under the wrong shop identity.

### Impact Explanation
This is a cross-tenant identity-attribution break directly caused by this gem's own webhook-verification design: the primitive it exposes for "verifying" a webhook does not bind the very identity fields (`shop`, `topic`, `webhook_id`) that downstream code is expected to trust. Since apps built on this gem are documented to route/store data keyed by `data.shop`, this can lead to cross-tenant data confusion or actions being taken against the wrong merchant's stored session/access token — matching the "cross-tenant access" impact class.

### Likelihood Explanation
Requires only: (1) the attacker to operate their own shop with the app installed (an ordinary unprivileged merchant/internet user under this app), (2) capturing one legitimate raw webhook body + `hmac-sha256` header sent to their own installed app instance, and (3) POSTing it again to the app's public webhook endpoint with a forged `shop-domain`/`topic`/`webhook-id` header. No knowledge of `api_secret_key` or any privileged credential is needed — the gem's own `Request`/`HmacValidator` code accepts it as valid.

### Recommendation
Bind the tenant-identifying fields into the signable string, or otherwise verify them out-of-band: include `shop`, `topic`, and `webhook_id` (not just the raw body) in the HMAC computation for webhook requests, or independently verify `request.shop` against an expected/known set of shop domains before constructing `WebhookMetadata`. At minimum, document prominently that `request.shop`/`topic`/`webhook_id` are unauthenticated and must not be trusted for tenant attribution without independent verification.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed.
# Shopify sends a legitimate webhook to the attacker's own endpoint:
#   body:    '{"id":123,"note":"hello"}'
#   headers: {
#     "shopify-hmac-sha256"  => "<valid HMAC of body using shared api_secret_key>",
#     "shopify-shop-domain"  => "attacker-shop.myshopify.com",
#     "shopify-topic"        => "orders/create",
#     "shopify-webhook-id"   => "real-id-1",
#     "shopify-api-version"  => "2024-01",
#   }
#
# Attacker replays the SAME body + SAME hmac-sha256 value, but swaps the shop header:
forged_headers = {
  "shopify-hmac-sha256" => captured_valid_hmac,     # unchanged, still validates
  "shopify-shop-domain" => "victim-shop.myshopify.com",  # forged
  "shopify-topic"       => "orders/create",
  "shopify-webhook-id"  => "real-id-1",
  "shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
``` [7](#0-6) [8](#0-7) [4](#0-3)

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
