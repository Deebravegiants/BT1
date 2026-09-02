### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` as plain accessors read directly from unauthenticated HTTP headers [1](#0-0) , but the value that is actually HMAC-signed and verified is only the raw request body:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (the raw body) and compares it to `verifiable_query.hmac`; it never touches `shop`, `topic`, or `webhook_id` [3](#0-2) .

`Registry.process` relies on this validation and then forwards the untouched `request.shop` field straight into `WebhookMetadata`, which is the tenant identifier handed to the app's business logic:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

`WebhookMetadata.shop` is documented as the tenant-identifying field consumed directly by the merchant app's handler [5](#0-4) .

This breaks the identity binding: `shop authenticated by HMAC` ≠ `shop stored/used as the tenant key`. The HMAC only binds `body ↔ secret`; it says nothing about which shop the body belongs to. Since every shop installation of the same app shares the same `api_secret_key`, a valid `(body, hmac)` pair produced for one shop remains valid for any `shop-domain` header value.

### Impact Explanation
Any user who can install the app on their own shop (an unprivileged/self-service action requiring no special privilege) can capture a genuine webhook delivery Shopify sends them — a real `(raw_body, X-Shopify-Hmac-Sha256)` pair signed with the app's shared secret — and replay that exact HTTP request to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` passes the attacker-chosen `shop` value straight through to the handler. If the host app uses `WebhookMetadata#shop` as the tenant key (the intended and documented use), this results in cross-tenant data corruption/misattribution: order/customer/product webhook payloads captured from the attacker's own shop get written into a victim shop's records, or mandatory compliance webhooks (`customers/redact`, `shop/redact`) can be forged against an arbitrary shop. This crosses the cross-tenant access boundary described as Critical impact.

### Likelihood Explanation
Requires only: (1) the ability to install the target app on any shop (self-service, unprivileged), (2) receiving one legitimate webhook delivery to capture a valid body/HMAC pair, and (3) the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a custom `shop-domain` header — no possession of `api_secret_key` or any victim credential is needed. This is a low-friction replay attack, not theoretical.

### Recommendation
Bind the shop identity into the value that is actually verified. Either (a) include `shop_domain`/`webhook_id`/`topic` in the signed material by concatenating them with the raw body before computing/verifying the HMAC in `Request#to_signable_string`, or (b) after `HmacValidator.validate` succeeds, cross-check `request.shop` against the shop recorded in the parsed body payload (Shopify webhook payloads typically include shop-scoped identifiers) or against the session/shop the webhook was registered for, rejecting mismatches before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal, unprivileged onboarding).
2. Shopify sends a legitimate webhook to the app: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for the app's shared `api_secret_key`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this raw HTTP request.
4. Attacker resends the identical request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` (`B`) only — unchanged — and it matches `H`, so validation passes [6](#0-5) .
6. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop = "victim-shop.myshopify.com"` even though the payload content actually belongs to the attacker's shop, and this is handed to the app's handler as if it were an authentic webhook from the victim [7](#0-6) .

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
