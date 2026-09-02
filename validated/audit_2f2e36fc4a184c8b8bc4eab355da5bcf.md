Found the identity-binding gap here: in `Webhooks::Request` (`lib/shopify_api/webhooks/request.rb`), the `hmac` used for HMAC verification is computed over `to_signable_string`, which is `@raw_body` only [1](#0-0) . The `shop`, `topic`, and `webhook_id` fields returned by the accessor methods are read directly from HTTP headers and are **not** part of the HMAC-signed bytes at all [2](#0-1) . The HMAC only proves the raw body was signed by Shopify; it says nothing about which shop the headers claim the webhook came from.

### Title
Webhook `shop` header is unauthenticated by HMAC, allowing shop-spoofing on genuine webhook deliveries - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Webhooks::Request#hmac` and `#to_signable_string` bind the HMAC signature only to `@raw_body`. The `shop` (and `topic`, `webhook_id`) values exposed by `Request#shop` / `#topic` / `#webhook_id` come from separate, unsigned HTTP headers (`shopify-shop-domain`, etc.), so `HmacValidator.validate` never checks that the claimed shop matches the body that was actually signed [3](#0-2) .

### Finding Description
The equality that should hold is: `shop attributed to the webhook by the host app` == `shop that Shopify actually signed the payload for`. `Utils::HmacValidator.validate` recomputes the HMAC solely from `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only the raw JSON body [1](#0-0) . The `shop` accessor is a plain header read with no connection to the signed bytes [4](#0-3) . Any component of the request that keys/dispatches webhook processing off `request.shop` (multi-tenant routing, per-shop secret/session lookup, per-shop rate limiting, logging) is trusting a value the gem never authenticated, even after `HmacValidator.validate` returns `true`.

### Impact Explanation
This is a cross-tenant identity-binding gap: the gem's own verification API (`HmacValidator.validate`) gives callers false confidence that `shop`/`topic`/`webhook_id` are trustworthy once it returns true, when in fact only the body is authenticated. A host application built directly on this gem's documented `Webhooks::Request` API (rather than a higher-level framework doing extra header pinning) that uses `request.shop` post-verification to select which tenant's data the body should be applied to can be made to process an HMAC-valid payload under an attacker-chosen shop identity, since only the request body needs to originate from a real, valid HMAC (e.g., replayed/relayed from any webhook a shop can trigger) while the shop header can be freely set by whoever relays/forwards the request to the app.

### Likelihood Explanation
Exploitability depends on the transport actually delivering attacker-controlled headers to the app (e.g., an intermediary/proxy, or any deployment where headers aren't independently pinned before reaching this code) alongside a validly-HMAC'd body. This is a plausible but non-trivial delivery path, and severity is bounded because the attacker cannot forge the HMAC itself, and this gem's `HmacValidator.validate` is a body-only check — it never claimed to authenticate headers, so this is more of a documented-boundary/likely-misuse issue than a full auth bypass.

### Recommendation
Include `shop`, `topic`, and `webhook_id` header values in `to_signable_string`, or otherwise document/enforce that `HmacValidator.validate` only authenticates the body and that callers must not trust `Request#shop`/`#topic`/`#webhook_id` for tenant-routing decisions without additional verification (e.g., cross-checking against the shop's known webhook secret/session before acting).

### Proof of Concept
1. Attacker relays/forwards a legitimately HMAC-signed webhook body (any shop can trigger a real webhook to obtain one) to the target app's webhook endpoint, but sets `X-Shopify-Shop-Domain` to a different, victim shop's domain.
2. `Webhooks::Request.new(raw_body:, headers:)` parses this without complaint (raw body and required headers all present) [5](#0-4) .
3. `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes the HMAC over `@raw_body`, which is untouched [6](#0-5) .
4. The host app, trusting `request.shop` because HMAC validation passed, applies the (unrelated-shop) body's data to the victim shop's tenant record.

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
