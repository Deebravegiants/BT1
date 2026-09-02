### Title
Webhook `shop` (and `topic`/`webhook-id`) header is trusted but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only the raw request body against the HMAC signature, but the `shop`, `topic`, `api_version`, and `webhook_id` values are read from HTTP headers that are excluded from the signed content. Any caller who can produce a request with a valid `(body, hmac)` pair can freely set the `shop-domain` header to any value and have the app's webhook handler process it as if it came from that shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` only compares `verifiable_query.hmac` against a signature computed over `to_signable_string` (the body), never over the headers: [3](#0-2) 

`Registry.process` trusts this validation, then builds `WebhookMetadata` directly from the unauthenticated header fields (`request.topic`, `request.shop`, `request.webhook_id`, `request.api_version`) and hands them to the application's registered handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no further validation (e.g. no `ShopValidator.sanitize!` call) before being passed to the handler: [5](#0-4) 

The identity binding that should hold is: **shop authenticated by the HMAC == shop delivered to the handler**. Because the HMAC only covers `@raw_body`, this equality is never enforced — the `shop-domain` header can diverge from whatever shop's secret actually produced the HMAC-signed body.

### Impact Explanation
Any unprivileged actor who operates their own Shopify shop that has this app installed (or who can otherwise legitimately trigger a webhook delivery bearing a genuine `hmac-sha256` value for a given body) can replay that exact `(body, hmac)` pair while substituting an arbitrary `shopify-shop-domain` (or `x-shopify-shop-domain`) header value pointing at a victim shop. `HmacValidator.validate` will still succeed because it only checks the body against the signature, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim's shop. This is a cross-tenant identity-binding break: application logic that persists or acts on webhook data keyed by `data.shop` (e.g., "process this shop's order/removal/redact event") can be poisoned with attacker-chosen body content misattributed to another merchant, corrupting per-tenant state or triggering shop-scoped side effects (e.g. GDPR "customers/redact", inventory/order updates) against a shop the attacker does not control.

### Likelihood Explanation
Likelihood is Medium: the attacker needs at least one genuine `(raw_body, hmac)` pair signed with the app's `api_secret_key` for *some* topic/body they control (trivially available to anyone who installs the app on their own dev/test store and triggers any webhook), and needs the app's webhook endpoint to be reachable over the internet (which it must be, by design, to receive Shopify webhooks). No access to the app's `client_secret`, access tokens, or any privileged account is required — only observation of one legitimate webhook delivery to their own store.

### Recommendation
Include the shop domain (and ideally the topic/webhook-id) inside the HMAC-signed content, or independently verify the `shop-domain` header against a trusted, previously-established value (e.g. the shop associated with the specific webhook subscription that Shopify registered, looked up server-side) before constructing `WebhookMetadata`. At minimum, document and enforce that `WebhookHandler` implementers must not trust `data.shop`/`data.topic` for authorization decisions without independently validating that the shop is a known, currently-installed shop (via `ShopValidator` and session lookup) rather than relying on the raw header value.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own store `attacker.myshopify.com`
#    and captures a legitimate webhook delivery, e.g.:
raw_body = '{"id": 1, "note": "hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)
# (This hmac is genuinely produced by Shopify for the attacker's own shop event.)

# 2. Attacker replays the SAME body+hmac but swaps the shop-domain header
#    to point at the victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled value
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. Registry.process succeeds because HmacValidator only checks raw_body vs hmac:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "orders/create",
#                                              shop: "victim-shop.myshopify.com",
#                                              body: {...attacker body...},
#                                              ...))
# The app's handler now processes attacker-controlled data
# as if it came from "victim-shop.myshopify.com".
```

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
