### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies the HMAC exclusively against the body bytes. The `shop` attribute, however, is read from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header and is never bound to (or cross-checked against) the HMAC-covered bytes. `Webhooks::Registry.process` passes this unauthenticated `shop` value straight into `WebhookMetadata`, which is handed to the app's handler as the tenant identifier for the event. This breaks the equality "shop authenticated == shop the handler acts on."

### Finding Description
`lib/shopify_api/webhooks/request.rb`:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end

def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`lib/shopify_api/utils/hmac_validator.rb` computes the signature over `verifiable_query.to_signable_string` and secure-compares it to the `hmac` header value: [2](#0-1) 

For a `Webhooks::Request`, `to_signable_string` is exactly `@raw_body` — it contains no reference to `shop`, `topic`, `webhook_id`, or `api_version`. Those fields come solely from HTTP headers and are not covered by the signature at all.

`Webhooks::Registry.process` validates the HMAC and then immediately trusts `request.shop` (the header value) as the tenant identity for the handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

Equality that should hold but doesn't:
`shop_covered_by_hmac == shop_the_handler_acts_on`

Before the request: for a genuine Shopify-delivered webhook, `shop-domain` header matches the shop whose data is in the signed body, and the HMAC secret is the app's shared `api_secret_key`.

After an attacker's replay: an unprivileged party who can capture or produce one valid `(raw_body, hmac)` pair (e.g., from their own installed shop's genuine webhook deliveries, which they fully control and can forward) can resend the identical body+HMAC to the app's webhook endpoint while substituting an arbitrary value in the `shopify-shop-domain` header. `HmacValidator.validate` still returns `true` (body unchanged), yet `WebhookMetadata#shop` now carries an attacker-chosen shop domain that has no cryptographic relationship to the HMAC-verified bytes.

### Impact Explanation
This is a cross-tenant identity binding break: the field the application actually keys its per-shop side effects on (`shop`) is not part of what the gem's own HMAC check authenticates. A host application that follows the documented `Registry.process` flow (using `WebhookMetadata#shop` to look up the tenant record, e.g. to attribute order/product/customer data, or to route GDPR `shop/redact`/`customers/redact` payloads) will process/store data under a shop identity chosen by the attacker rather than the shop that the signed payload actually originated from. This matches the Critical "cross-tenant access" category in scope.

### Likelihood Explanation
Any user capable of installing the app on their own shop (an "unprivileged internet user" with respect to any other tenant) can capture/replay a legitimate `(body, hmac)` pair for their own shop's webhooks and freely vary the `shop-domain` header, since it is never validated against the signed content. No access token, `api_secret_key`, or privileged account is required — only participation as an ordinary merchant/installer, which any internet user can do by installing a public app. This is fully reachable through the gem's documented `Webhooks::Registry.process` API exactly as intended to be used.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) identity to the HMAC-verified content, or otherwise require the host application to independently verify that the `shop-domain` header corresponds to a shop with an active installation/session before trusting it — and document this requirement prominently, since currently nothing in `Webhooks::Request`/`Registry` enforces or even warns about it. At minimum, `HmacValidator`/`Webhooks::Request#to_signable_string` should not present `shop` as if it were part of a verified payload without callers being explicitly warned that it is header-derived and unauthenticated.

### Proof of Concept
1. Merchant M installs the app on `attacker-shop.myshopify.com` and receives a genuine webhook delivery with raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`).
2. M replays the exact same request to the app's webhook endpoint, changing only the header `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which checks `HMAC-SHA256(api_secret_key, B) == H` — this still passes because `B` and `H` are unchanged. [4](#0-3) 
4. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <M's data>, ...)`. [5](#0-4) 
5. Any application logic keyed on `data.shop` (e.g., updating the victim's stored records, or handling `shop/redact`) is executed against the wrong tenant, using data supplied by the attacker.

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
