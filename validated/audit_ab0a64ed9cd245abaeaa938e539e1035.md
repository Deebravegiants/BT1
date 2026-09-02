### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so `ShopifyAPI::Utils::HmacValidator.validate` only proves the integrity/authenticity of the body bytes. The `shop` (and `topic`/`webhook_id`) values, which are taken from HTTP headers, are never included in the signed content, yet `Registry.process` trusts `request.shop` as the tenant identity handed to the app's webhook handler.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`, i.e. the HMAC binding is `HMAC(secret, body)`. The `shop` field, sourced from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header, is not part of this signed string: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally forwards `request.shop` (and `request.topic`, `request.webhook_id`) to the registered handler as the tenant identity for the payload: [4](#0-3) 

The identity binding that should hold is: `shop asserted to the handler == shop that produced the signed body`. Because the HMAC only covers the body, this equality is never checked — `HmacValidator.validate_signature` only compares `computed_signature = HMAC(secret, body)` against the received signature, with no dependency on `shop`: [5](#0-4) 

Since every merchant that installs the same app receives webhooks signed with the same shared `client_secret` (`Context.api_secret_key`), an unprivileged attacker who runs the app on their own store (a routine, unprivileged action requiring no special credentials) can capture a legitimate `(raw_body, hmac)` pair for their own shop and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` because the signature check never inspects the header, and `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the forged victim domain while `body` is the attacker's own (potentially attacker-controlled) shop data.

### Impact Explanation
This breaks the shop-identity binding used by `ShopifyAPI::Webhooks::Registry.process` → `WebhookHandler#handle`. Any host application that uses `data.shop` from `WebhookMetadata` (the gem's documented usage pattern, e.g. `perform_later(shop_domain: data.shop, webhook: data.body)` shown in `docs/usage/webhooks.md`) to route or persist webhook data to a tenant record will accept attacker-supplied data under a victim shop's identity — a cross-tenant data-confusion/injection primitive achievable by any merchant that installs the app, without needing the app's `client_secret`, an access token, or the victim's credentials.

### Likelihood Explanation
High practical likelihood for any app relying on this gem's webhook processing exactly as documented: the attacker only needs to (1) install the app on any shop they control to receive genuinely signed webhooks, and (2) send an HTTP POST to the app's webhook endpoint with the captured body/HMAC and a forged `shop-domain` header — no secrets, tokens, or privileged access are required, and the code path performs no additional binding check.

### Recommendation
Do not treat `request.shop` as authenticated. If shop identity must be asserted from the webhook request, cross-check it against a shop known to be associated with an active/valid installation (e.g., looked up via a stored session for that shop), or have `Registry.process` require callers to supply the expected shop and compare it, rather than trusting the header value as ground truth. At minimum, document prominently that the `shop` header is not covered by the Shopify webhook HMAC and must be independently corroborated by the host app before being used for tenant-identifying operations.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets the app register e.g. the `orders/create` topic.
2. Shopify sends a legitimate webhook to the app's endpoint: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `(B, HMAC(secret, B))` (they can read their own webhook payloads, e.g. via a proxy or by having the app log them).
4. Attacker replays a POST to the same endpoint with the identical body `B` and identical `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)` which recomputes `HMAC(secret, B)` — unaffected by the header change — and returns `true`.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop. [4](#0-3) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
