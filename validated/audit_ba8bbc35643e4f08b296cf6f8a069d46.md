This confirms the vulnerability. Comparing the two `VerifiableQuery` implementations shows the asymmetry clearly:

- `ShopifyAPI::Auth::Oauth::AuthQuery#to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:34-43`) explicitly includes `shop` inside the HMAC-signable string — the shop identity is cryptographically bound to the signature.
- `ShopifyAPI::Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) returns only `@raw_body`. The `shop` value (`request.shop`, line 21-23) comes from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is **never included** in the HMAC computation performed by `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:27-31`), which only signs `verifiable_query.to_signable_string`.

`Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) validates the HMAC and then immediately trusts `request.shop` to build `WebhookMetadata` (`lib/shopify_api/webhooks/webhook_handler.rb:6-12`), passing it to the host app's `handler.handle`. The binding the code implicitly assumes is `hmac_valid(body) ⟺ shop_header_is_authentic`, but the equality that actually holds is only `hmac_valid(body) ⟺ body_is_authentic`. The `shop` header is fully attacker-controllable independent of the signature.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body, while `ShopifyAPI::Webhooks::Registry.process` uses the unsigned `shopify-shop-domain` header as the tenant identity passed to the host application's webhook handler.

### Finding Description
`Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-31`) computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` value. For webhook requests, `to_signable_string` returns `@raw_body` only [1](#0-0) . Meanwhile `shop` is read straight from an HTTP header with no cryptographic tie to the signature [2](#0-1) .

`Webhooks::Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop` as the tenant-scoping field handed to the app's handler [3](#0-2) . Contrast this with the OAuth callback `AuthQuery`, where `shop` is deliberately part of the signed string [4](#0-3) , showing the library's own pattern for what "properly bound" identity should look like — a pattern not followed for webhooks.

The broken identity binding, as an equality: the code assumes `hmac_valid(raw_body) ⟺ shop_header_authentic`, but only `hmac_valid(raw_body) ⟺ raw_body_authentic` actually holds. `shop` is fully attacker-controlled and independent of the signed content.

### Impact Explanation
An unprivileged actor who has installed the app on their own store (or who can otherwise obtain one genuine, validly-HMAC-signed webhook body/HMAC pair for any shop, e.g. via their own store's legitimate webhook deliveries) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. Because the header isn't covered by the signature, `HmacValidator.validate` still returns `true`, and `Registry.process` will invoke the host app's handler with `WebhookMetadata#shop` set to the victim's domain. If the host app's handler uses this `shop` field to look up sessions, update tenant-scoped data, or take shop-scoped actions (the intended and documented usage of `WebhookMetadata`), this results in cross-tenant data corruption/access — a Critical-class impact per the crossing of a tenant/authentication boundary.

### Likelihood Explanation
Requires the attacker to control at least one shop with the app installed (or otherwise capture a valid raw_body+HMAC pair) — a normal, unprivileged step available to anyone who can install a Shopify app. No secrets, tokens, or privileged access are required; only a header value needs to be forged in an HTTP request to the app's own publicly reachable webhook endpoint.

### Recommendation
Bind the shop-domain (and ideally topic/api-version/webhook-id) into the value that is HMAC-verified, or independently authenticate that the shop header matches an installation known to have legitimately triggered this specific `raw_body`/HMAC pair before trusting it in `WebhookMetadata`. At minimum, document and encourage host apps to cross-check the incoming `shop` against a shop-specific webhook signing arrangement, but the more robust fix is inside this gem: extend `Webhooks::Request#to_signable_string` (or `HmacValidator`) to incorporate the shop/topic/webhook_id headers into the signed payload comparison, consistent with how `Auth::Oauth::AuthQuery` binds `shop` into its signable string.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a normal, unprivileged onboarding step) and receives a legitimate webhook, e.g. `orders/create`, with a real `x-shopify-hmac-sha256` header computed over the raw JSON body using the app's `api_secret_key`.
2. Attacker replays the identical raw body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers successfully (all required headers present) [5](#0-4) .
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC is computed only over `@raw_body`, which is unchanged [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own store and Shopify never sent this webhook for the victim [7](#0-6) .

### Citations

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
