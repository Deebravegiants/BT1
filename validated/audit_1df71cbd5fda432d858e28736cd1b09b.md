## Title
Webhook `shop` and `topic` identity fields are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook delivery solely by validating an HMAC over the raw request body, then dispatches to a handler using the `topic` and `shop` values, both of which are read from HTTP headers that are never included in the HMAC signature computation.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC exclusively against that signable string [2](#0-1) . Meanwhile `Request#shop` and `Request#topic` are pulled directly from the `shopify-shop-domain` / `x-shopify-shop-domain` and `shopify-topic` / `x-shopify-topic` headers with no cryptographic binding to the HMAC [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts these unauthenticated header values: it looks up the handler by `request.topic` and forwards `request.shop` into the handler's `WebhookMetadata` as the tenant identifier for the delivery [4](#0-3) .

The identity binding that should hold is:
`bytes verified by HMAC == bytes the shop/topic identity is derived from`

Here that equality is broken: the HMAC verifies `raw_body` only, while `shop` and `topic` — the values a host application will use to determine *which merchant* the webhook is for and *which handler* to invoke — are taken from headers outside that signed scope.

### Impact Explanation
Any unprivileged caller who has (or forges) a single valid `(raw_body, hmac)` pair for the app's secret — e.g., by replaying/observing one legitimate webhook delivery from any shop, or by simply supplying a body they generated when the app itself is misconfigured to accept externally-supplied bodies — can resubmit the identical body/HMAC pair while swapping the `shopify-shop-domain` and/or `shopify-topic` headers to arbitrary values. `Registry.process` will still consider the HMAC valid (since it never depended on those headers) and will hand the host application a `WebhookMetadata` claiming the event belongs to a different shop or topic than the one the signature actually vouches for. Since host applications commonly key their session/data lookups off `WebhookMetadata#shop`, this can result in cross-tenant confusion: data intended for shop A being processed under shop B's identity, or a handler for an unintended topic being invoked with attacker-controlled routing. This maps to a cross-tenant identity boundary crossing, which is a Critical-impact category per the given scope.

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP POST to the app's webhook endpoint with any previously-observed valid `(body, hmac)` pair (no access token, API secret, or privileged account is needed — the gem's own header parsing has no defense against header substitution). Because Shopify's own webhook delivery infrastructure typically keeps `shop`/`topic` and `hmac` consistent, this is not exploitable against Shopify's real deliveries directly, but any process that can influence or replay a raw body/HMAC pair (proxies, logging/replay tooling, or a compromised/malicious third party with visibility into any single webhook payload for any shop) can trivially forge the shop/topic association because the gem itself performs no check that the asserted headers correspond to the signed body.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (in addition to the body) in the signable string used for HMAC verification inside `Request#to_signable_string`, or otherwise cryptographically bind these header-derived identity fields to the signature before they are trusted and forwarded to `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Obtain one legitimate webhook delivery to the app for `shop-a.myshopify.com`, topic `orders/create`, with raw body `B` and header `x-shopify-hmac-sha256: H` (H is valid for `B` under the app's secret).
2. Replay the same request to the app's webhook endpoint, but change `x-shopify-shop-domain` to `shop-b.myshopify.com` (or any other topic in `x-shopify-topic`), keeping body `B` and header `H` unchanged.
3. `Utils::HmacValidator.validate(request)` succeeds because it only re-computes the HMAC over `raw_body` [1](#0-0) [5](#0-4) .
4. `Registry.process` then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied `shop-b.myshopify.com` value [6](#0-5) , even though the HMAC never vouched for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
