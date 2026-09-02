### Title
Webhook shop-domain (tenant identity) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates an incoming webhook only by checking `Utils::HmacValidator.validate(request)`, which in turn signs/verifies `request.to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw HTTP body [1](#0-0) . The `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` values are all read directly from unauthenticated HTTP headers and are never included in the signed content [2](#0-1) . `Registry.process` nonetheless passes the unauthenticated `request.shop` straight to the app's webhook handler as the identity of the shop the payload belongs to [3](#0-2) .

### Finding Description
This mirrors the M-13 bug class: a check (`HmacValidator.validate`) is treated as if it authenticates the whole request, but a field that is actually *acted on* downstream — here, the `shop` header used to attribute the webhook to a tenant — is not part of what the check covers.

Concretely:
- `HmacValidator.validate` computes `computed_signature = compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` field of the request [4](#0-3) .
- For a webhook `Request`, `to_signable_string` is simply `@raw_body` [1](#0-0) , and `hmac` is parsed from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header [5](#0-4) .
- `shop`, `topic`, `webhook_id`, and `api_version` are read from separate headers (`shopify-shop-domain`, etc.) that are **not included** in the signable string [6](#0-5) .
- `Registry.process` validates the HMAC and then unconditionally forwards `request.shop` (and the other unauthenticated headers) to the app-defined handler via `WebhookMetadata` [3](#0-2) .

The equality that is expected to hold is: `shop the HMAC was computed for == shop the handler attributes the payload to`. In practice, only the body bytes are bound by the HMAC; the shop-domain header is unauthenticated and can be freely modified without invalidating the signature. The gem's own documentation instructs integrators to treat `data.shop` as *the shop domain of the webhook*, i.e., as an authenticated tenant identifier [7](#0-6) , which this implementation does not guarantee.

### Impact Explanation
Any merchant who has a legitimate installation of the app (an unprivileged actor with no access to `api_secret_key`) receives genuine webhooks — each a valid `(raw_body, hmac)` pair signed with the app's secret for their own shop. Because the header carrying the shop domain is outside the signed content, that merchant can replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a different (victim) shop's domain. `HmacValidator.validate` still succeeds (the body is unchanged), and the app's registered handler receives `WebhookMetadata` claiming the payload originates from the victim shop. Any host application that uses `data.shop` to look up/update per-tenant records (as the documentation recommends) will therefore process attacker-controlled, replayed webhook data under a shop it does not actually belong to — a cross-tenant data-integrity/impersonation issue.

### Likelihood Explanation
Likelihood is moderate to high: the only prerequisite is that the attacker has previously received one legitimate webhook for their own shop (trivial for any merchant with the app installed) and can send an HTTP POST with modified headers to the app's public webhook endpoint — no access to `api_secret_key`, tokens, or any other privileged credential is required.

### Recommendation
Bind the tenant identity to the HMAC-protected content instead of trusting the unauthenticated `shop-domain` header in isolation. At minimum, the library should either (a) include the shop domain (and topic/webhook id) in the signable string used for HMAC validation, or (b) require/encourage callers to independently verify that `request.shop` corresponds to a shop with a known, previously-established session/webhook registration before dispatching to the handler, and clearly document that the header-derived `shop` value is not itself authenticated by the HMAC check.

### Proof of Concept
```ruby
# Attacker is a merchant with the app installed on "attacker-shop.myshopify.com"
# and has captured one legitimate webhook delivery for their own shop:
raw_body = '{"id":123,"note":"hello"}'
valid_hmac = "<captured shopify-hmac-sha256 header value for raw_body>"

# Attacker replays the identical body/hmac but swaps the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,          # still valid: HMAC only covers raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled, unsigned
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) passes (only raw_body is checked),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)) is invoked,
#    even though this payload never originated from Shopify for victim-shop.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
