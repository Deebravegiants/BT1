This confirms the finding: `ShopifyAPI::Webhooks::Registry.process` verifies the request via `Utils::HmacValidator.validate(request)`, whose signature is computed exclusively over `Request#to_signable_string`, i.e., `@raw_body` [1](#0-0) . The `shop` field returned by `Request#shop`, however, is read straight from the unsigned `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) , and it is this same unauthenticated value that `Registry.process` forwards as the tenant identifier to the app's handler via `WebhookMetadata#shop` [3](#0-2) . The docs explicitly instruct host apps to trust `data.shop` as "The shop domain of the webhook" for dispatching per-tenant work [4](#0-3) .

### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw body, while the `shop` value used to attribute that body to a tenant is taken from an HTTP header that is excluded from the signed payload. This breaks the equality that should hold between "the shop whose secret validated this request" and "the shop the gem tells the host app the data belongs to."

### Finding Description
`Utils::HmacValidator.validate(verifiable_query)` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` accessor [5](#0-4) . For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , and `hmac` is likewise derived only from the `hmac-sha256` header [6](#0-5) . Neither the topic, webhook id, api-version, nor — critically — the `shop-domain` header participates in the signed string.

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (parsed from the unsigned header) as the tenant to attribute the event to:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [3](#0-2) 

The identity binding that should hold is: `shop that authenticated the HMAC == shop attributed in WebhookMetadata`. Because `shop` is read from an unsigned header, an attacker who possesses one *validly-HMAC-signed* webhook body/signature pair for their own store (any developer/merchant can install the app on a store they control and legitimately receive genuine Shopify webhooks) can replay that exact `raw_body` + `hmac-sha256` value to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for an arbitrary victim shop. `HmacValidator.validate` still returns `true` because the signature check never inspects the header, so `Registry.process` dispatches the attacker-supplied body to the handler labeled as belonging to the victim tenant.

### Impact Explanation
This is a cross-tenant identity binding failure: an unprivileged internet user who merely operates their own (possibly free/dev) shop installation of a public app can inject webhook payloads that the host application will process as though they originated from a shop the attacker does not control. Depending on how the host app uses `data.shop` (as documented, it is expected to key per-tenant job dispatch, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [7](#0-6) ), this allows cross-tenant data injection/corruption without needing the victim's credentials, the app's `client_secret`, or any privileged access — satisfying the Critical cross-tenant-access bar.

### Likelihood Explanation
Likelihood is high for any app that: (1) is public or otherwise installable by an attacker-controlled store, and (2) relies on `ShopifyAPI::Webhooks::Registry.process` / `WebhookMetadata#shop` for tenant attribution as documented. The webhook HTTP endpoint is by design internet-reachable and unauthenticated beyond the HMAC check, and the attacker only needs one genuine webhook delivery to their own store to obtain a valid `(raw_body, hmac)` pair to replay with a swapped header.

### Recommendation
Do not treat `request.shop` as trusted tenant context unless it is cryptographically bound to the signed payload. Either include the shop domain (and ideally topic/webhook id) in the signable string used by `HmacValidator`, or independently verify that the shop asserted in the header matches a shop for which the app holds an active, previously-established webhook registration/session before dispatching to the handler. At minimum, document prominently that `data.shop` is unauthenticated header data and must not be used as a sole tenant-scoping key without additional verification against known registered shops.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com` and lets Shopify deliver one genuine webhook (e.g. `orders/create`) to the app's registered endpoint, capturing the exact `raw_body` and the `X-Shopify-Hmac-Sha256` header value Shopify computed with the app's real `client_secret`.
2. Attacker replays an HTTP POST to the same public webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and finds it matches — validation succeeds [8](#0-7) .
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled parsed body>, ...)`, causing the host app to process attacker-supplied data under the victim tenant's identity [9](#0-8) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
