### Title
Webhook `shop`, `topic`, and `webhook-id` are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw request body. The shop, topic, and webhook id that the handler acts on are read directly from HTTP headers that are never included in the signed material, so they are not bound to the signature at all.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic protection [2](#0-1) . `Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, to_signable_string)` (i.e., `HMAC(secret, raw_body)`) and compares it to the `hmac` header [3](#0-2) [4](#0-3) . After that single check succeeds, the registry immediately builds `WebhookMetadata` and dispatches it to the app's handler using `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the signed bytes [3](#0-2) .

The identity binding that should hold is:
`bytes verified by HMAC == bytes the handler attributes to a given shop/topic`

Here it does not: `HMAC covers raw_body` but `handler acts on shop-domain/topic/webhook-id headers`, which are disjoint fields. Since the app's `api_secret_key` is shared across all shops using the same webhook endpoint, any tenant who has legitimately received one authentic webhook (body `B`, valid `hmac H` for `B`) can replay that exact `(B, H)` pair to the same endpoint while substituting `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) headers naming a different, victim shop. `HmacValidator.validate` will still succeed because it never inspects the headers, and `Registry.process` will hand the forged shop/topic attribution to the app's handler as if Shopify itself had sent it for that tenant.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: it allows a low-privilege actor who merely operates their own installed shop to inject webhook events attributed to an arbitrary victim shop (cross-tenant access), potentially causing the host application to write attacker-controlled data into another merchant's records, trigger sensitive per-shop side effects (e.g., mandatory `customers/redact`, `shop/redact` handlers), or corrupt per-shop state keyed by `shop`. This matches the report's bug class ("field acted on but not covered by the HMAC") and satisfies the Critical/High bar of cross-tenant access.

### Likelihood Explanation
Exploitability only requires the attacker to install the app on their own shop (a normal, unprivileged interaction) and observe one legitimate webhook delivery from Shopify to capture a valid `(raw_body, hmac)` pair — no access to `api_secret_key` or any privileged credential is needed. The replay is a straightforward HTTP POST with attacker-controlled headers, since headers are trivially forgeable by any caller who can reach the webhook endpoint directly.

### Recommendation
Include the identity-critical fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified material, or otherwise cryptographically bind them to the payload before dispatch (e.g., validate against an independently retrieved/authenticated topic-registration record, or require Shopify's actual signed webhook envelope format that covers these fields). At minimum, cross-check `request.shop` against an expected/allow-listed value tied to the registration before invoking the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets it receive a genuine webhook, capturing the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` from that delivery (both attacker-observable, since it's their own shop's traffic).
2. Attacker sends a forged POST to the app's webhook endpoint:
   - Body: `B` (unchanged)
   - Headers: `X-Shopify-Hmac-Sha256: H` (unchanged), `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged), `X-Shopify-Topic: <same or different registered topic>` (forged), `X-Shopify-Webhook-Id: <arbitrary>` (forged).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (headers only need to be present, per [5](#0-4) ).
4. `ShopifyAPI::Webhooks::Registry.process(request)` computes `HMAC(secret, B)`, which equals `H` (since `B`/`H` is a real, previously valid pair), so validation passes [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(topic: forged_topic, shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)` [7](#0-6) , causing the host application to process attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
