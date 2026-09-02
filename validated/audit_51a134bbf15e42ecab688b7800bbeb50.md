### Title
Webhook shop-tenant identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the `shop-domain` header (and `topic`/`webhook-id`) taken from unauthenticated headers to build the `WebhookMetadata` handed to the app's handler. Because the shop identity is never part of the signed content, an entity that can obtain one valid `(body, hmac)` pair signed with the app's shared `client_secret` can replay it with an arbitrary `shop-domain` header and have it accepted as an authentic webhook "from" a different shop.

### Finding Description
`Utils::HmacValidator.validate` computes `computed_signature = compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, and `webhook_id` are read directly from HTTP headers without any cryptographic binding to the signature [3](#0-2) .

`Registry.process` performs only this body-HMAC check, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) as authenticated tenant identity and passes them straight into the handler: `Utils::HmacValidator.validate(request)` ... `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) . `WebhookMetadata.shop` is documented as "The shop domain of the webhook" [5](#0-4) , and the library's own documentation states this call "will verify the request did indeed come from Shopify" before invoking the handler [6](#0-5) , i.e., the gem promises that the resulting `data.shop` is an authenticated identity, but the code cannot deliver that guarantee since `shop` is outside the HMAC's scope.

The identity binding that is broken, expressed as an equality that must hold but does not:
`shop_bound_by_hmac(raw_body, hmac) == shop_header_used_for_tenant_routing(request)`

Because the app's `client_secret` (used to compute the HMAC) is shared across every shop that has installed the app, any merchant who has installed the app can legitimately receive a real, validly-signed webhook for their own store, capture the `(raw_body, X-Shopify-Hmac-Sha256)` pair, and re-POST it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop. `HmacValidator.validate` will accept it because the signature only covers `raw_body`, and `Registry.process` will dispatch it to the handler labeled with the victim's shop.

### Impact Explanation
This crosses a tenant boundary: an unprivileged holder of one valid installation of the app can forge webhook events attributed to a different (victim) shop. Any host application that uses `data.shop` from `WebhookMetadata` to scope database writes, trigger per-tenant business logic, or make authorization decisions (the exact intended and documented usage pattern of this gem) will process attacker-controlled data as if it originated from the victim tenant — meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Requires only that the attacker be a legitimate (even free/trial) installer of the target Shopify app — no access to `api_secret_key`, access tokens, or privileged accounts is needed, and the webhook endpoint is a plain public HTTP route by design. Capturing one's own valid webhook `(body, hmac)` pair and replaying it with a modified header is trivial once the attacker controls their own shop's webhook deliveries.

### Recommendation
Bind the identity fields to the signed content, not just headers: include `shop`, `topic`, and `webhook_id` in the HMAC-covered signable string (or verify `request.shop` against the specific shop session/subscription the webhook was registered for), rather than validating HMAC over `raw_body` alone in `to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`). At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated and must be independently cross-checked by the host app against known installed shops before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and registers/receives a webhook (e.g. `orders/create`) for it — Shopify signs the raw body with the app's shared `client_secret`, giving the attacker a real `(raw_body, X-Shopify-Hmac-Sha256: H)` pair.
2. Attacker sends `POST <app_webhook_path>` directly to the app's webhook endpoint with:
   - `raw_body` = the captured body
   - `X-Shopify-Hmac-Sha256` = `H`
   - `X-Shopify-Shop-Domain` = `victim.myshopify.com` (any target shop, real or fabricated)
   - `X-Shopify-Topic` = `orders/create`
3. `ShopifyAPI::Webhooks::Request.new` parses these headers [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` and succeeds because `H` is a genuinely valid signature for that body under the shared secret [8](#0-7) .
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "orders/create", body: ...)`, and the host app processes/stores this as authentic data for `victim.myshopify.com`, achieving cross-tenant data injection/spoofing.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
