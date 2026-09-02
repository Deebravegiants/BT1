Confirmed: `Registry.process` at `lib/shopify_api/webhooks/registry.rb:189-200` validates the request via `Utils::HmacValidator.validate(request)`, but that HMAC only signs `request.to_signable_string` (the raw body), which is defined in `lib/shopify_api/webhooks/request.rb:35-38` as `@raw_body`. The `shop` (and `topic`, `webhook_id`, `api_version`) values come from the `shopify-shop-domain` header via `shopify_header`, which is never included in the signable string in `lib/shopify_api/utils/hmac_validator.rb:26-31`. The trusted `WebhookMetadata.shop` passed to the host app's handler (`registry.rb:198`) is therefore taken from a field entirely outside the HMAC's coverage.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant relabeling of a validly-signed webhook body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from raw, unauthenticated HTTP headers, while `to_signable_string` (the data actually covered by the HMAC) is only the raw request body. `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` and compares it to the value parsed out of the `shopify-hmac-sha256` header. Because the header set (`shop-domain`, `topic`, `webhook-id`, `api-version`) is disjoint from the signed body, an attacker who possesses one validly-signed webhook body+HMAC pair for their own shop can replay it with a different `shopify-shop-domain` header value and have `Registry.process` accept it as valid and construct a `WebhookMetadata` claiming an arbitrary `shop`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate_signature` computes the HMAC solely over that signable string and constant-time-compares it against `request.hmac`, which is itself pulled straight from the `hmac-sha256` header: [2](#0-1) [3](#0-2) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from headers via `shopify_header`, none of which participate in the signature: [4](#0-3) 

`Registry.process` trusts `request.shop` (and `request.topic`) once `HmacValidator.validate` returns true, and forwards it directly into `WebhookMetadata`, which is handed to the app's `WebhookHandler#handle`: [5](#0-4) 

The binding that should hold is: `shop` authenticated by the HMAC == `shop` acted on by `WebhookMetadata`/the handler. Because the header carrying `shop` is outside `to_signable_string`, this equality is not enforced — the gem verifies "this body byte sequence was HMAC'd by Shopify with our secret" but not "this body was HMAC'd *for this shop*". Any body+HMAC pair valid for shop A can be resent with the `shopify-shop-domain` header rewritten to shop B, and `Registry.process` will still call `Utils::HmacValidator.validate(request)` successfully and dispatch `handler.handle` with `shop: "B"`.

### Impact Explanation
This lets an unprivileged attacker who legitimately receives webhooks for their own store (a standard, unprivileged capability of any merchant/installer of the app) relabel a validly-HMAC'd payload as belonging to a different, victim shop before it reaches the app's webhook handler. Depending on how the host app trusts `WebhookMetadata.shop` (e.g., to select which merchant's session/data to update, as the docs and `webhook_handler.rb` `WebhookMetadata` struct imply it should), this enables cross-tenant data confusion/injection: an attacker-controlled payload (subject to the shape of a real webhook topic body) can be attributed to an arbitrary target shop domain, since the shop identity is trusted without being part of the signed material.

### Likelihood Explanation
Likelihood is limited by two factors: the attacker needs a validly-signed body+HMAC pair to begin with (trivially available — any app installer receives real webhooks with valid HMACs for their own shop), and they need network-level ability to POST that replayed request to the app's webhook endpoint with a modified `shopify-shop-domain` header (no credentials required, since HMAC validation succeeds). No `api_secret_key` or access token is needed by the attacker. This is a realistic path for any public-facing webhook endpoint built on this gem.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them, e.g. by validating them against Shopify's own out-of-band registration records) so that the HMAC covers the full set of trusted fields, not just the raw body. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate the header-derived `shop` value so `HmacValidator.validate` fails if the shop is altered independently of the body.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and raw JSON body `B`.
2. Attacker resends the exact same body `B` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — this matches, since the body wasn't changed.
4. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: ..., ...))`, causing the app to process attacker-supplied `orders/create` data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
