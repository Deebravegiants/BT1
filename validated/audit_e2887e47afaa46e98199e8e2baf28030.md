This confirms the finding: `ShopifyAPI::Webhooks::Request#hmac` is verified only over the raw body, and the `shop` (and `topic`, `webhook_id`, `api_version`) values are read straight from HTTP headers that are never included in the signed payload. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` (tenant identity) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header as the tenant identity passed to the host app's handler. Because the shop header is never part of the signed material, any party capable of producing one valid `(body, hmac)` pair for the app's shared `client_secret` can replay that pair with an arbitrary `shop` header value, causing the host application to process/attribute the webhook to a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the HMAC strictly over that signable string using `Context.api_secret_key`, which is the app's single, shop-independent secret shared across every merchant that installs the app: [5](#0-4) 

Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers that are not part of `to_signable_string`: [6](#0-5) 

`Registry.process` raises only if the HMAC check fails, then forwards the untrusted `request.shop` value straight into `WebhookMetadata`, which is documented as "The shop domain of the webhook" and is the identity host apps use to scope tenant data: [4](#0-3) [7](#0-6) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop_bound_by_hmac == shop_delivered_to_handler`

In reality the left side is undefined (the header isn't in the signed bytes) while the right side is attacker-controlled, since any unprivileged user who has installed the app on their own store legitimately receives valid `(body, hmac)` pairs signed with the shared `client_secret`, and can resend that exact body/hmac pair to the app's webhook endpoint with a forged `shop-domain` header naming any other shop domain.

### Impact Explanation
This breaks the shop/tenant authentication boundary that host apps rely on `WebhookMetadata#shop` for (e.g., to select the DB row/session/tenant to update). An attacker who is a legitimate merchant of the app (an "unprivileged internet user" from the app's perspective) can spoof webhooks appearing to originate from any other shop domain, since the same `client_secret` signs webhooks for all shops. Depending on how the host app uses `data.shop`, this enables cross-tenant data corruption or unauthorized actions attributed to a victim's shop — a cross-tenant access issue.

### Likelihood Explanation
Likelihood is high for any app author who follows the gem's documented webhook handler pattern, since `WebhookMetadata#shop` is the only tenant identifier provided by the library and its own docs advertise using it directly (`data.shop`) to key work: [8](#0-7)  No additional secret or privileged access is needed beyond having one's own shop install the app (a normal, unprivileged path).

### Recommendation
Include the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) in the HMAC-signed material verified by `HmacValidator`, or otherwise cryptographically bind the `shop` value to the webhook payload before exposing it via `WebhookMetadata`. At minimum, document prominently that `data.shop` is unauthenticated and must not be trusted as a tenant key without additional verification (e.g., cross-checking against a known/expected shop for the registered webhook).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers/receives a legitimate webhook, capturing the raw body `B` and the corresponding `x-shopify-hmac-sha256` header `H` (valid because `H = HMAC-SHA256(client_secret, B)`, and `client_secret` is the same for all shops using the app).
2. Attacker sends a POST to the app's webhook endpoint with:
   - body = `B`
   - header `x-shopify-hmac-sha256` = `H`
   - header `x-shopify-shop-domain` = `victim-shop.myshopify.com` (arbitrary)
   - header `x-shopify-topic` = same/any registered topic
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [3](#0-2) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [9](#0-8) , causing the host application to act as though the (attacker-controlled) payload `B` came from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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

**File:** docs/usage/webhooks.md (L19-27)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
