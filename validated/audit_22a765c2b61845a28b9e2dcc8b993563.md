### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` to let `HmacValidator` authenticate incoming webhooks, but the signable string used for HMAC verification is only the raw request body — never the `shop-domain` header that identifies which tenant the webhook belongs to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop` is derived purely from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, with no cryptographic binding to the signed payload: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it authenticates the JSON body only: [3](#0-2) 

This mirrors the reported bug class of "a field acted on but not covered by the HMAC": the `shop` identity value that a host application uses to attribute the webhook to a specific merchant/tenant is not part of the signed material, only `topic`/`hmac-sha256`/`shop-domain` headers being *present* is checked, not that `shop-domain` is *authentic*: [4](#0-3) 

Because a Shopify app's webhook HMAC is signed with the app's single `client_secret` (shared across every shop that installs the app, not shop-specific), any actor able to install the app on their own shop and observe one legitimately-signed webhook (raw body + valid HMAC) obtains a signature that Shopify's Ruby library will accept for that same body regardless of which `shop-domain` header accompanies it. An attacker can then submit a request bearing the original valid `hmac-sha256`/body pair but with the `shop-domain` header rewritten to a victim shop's domain. `ShopifyAPI::Webhooks::Registry.process` (and any host app relying on `request.shop` from a passing `HmacValidator.validate` check) would treat the forged shop as authentic, letting an unprivileged attacker inject or attribute events to a shop they do not control — a cross-tenant boundary crossing that breaks the equality: `shop asserted by header == shop actually authenticated by HMAC`, which the code silently equates.

### Impact Explanation
This falls under "cross-tenant access": a host application built on this gem that trusts `Webhooks::Request#shop` for tenant routing/attribution after `HmacValidator.validate` succeeds can be tricked into associating attacker-controlled webhook data with a victim shop, since the shop value is never part of the HMAC-protected payload.

### Likelihood Explanation
Requires only: (1) the attacker installs the target app on their own (even free/dev) Shopify store to receive one legitimately HMAC-signed webhook for a body they can choose/predict, and (2) the ability to send an arbitrary HTTP request to the host application's public webhook endpoint with a modified `shop-domain` header while replaying the original body+HMAC — no access token, `client_secret`, or privileged account is required, matching the "unprivileged internet user" threat model.

### Recommendation
Include the `shop-domain` (and ideally `topic`) header values in the signable material verified by the HMAC (or otherwise cryptographically bind them to the signed body), so `HmacValidator.validate` fails if any of these Shopify-supplied identity fields have been altered in transit. At minimum, document that `Request#shop` must never be trusted for tenant routing/authorization without an independent, out-of-band verification (e.g., cross-checking against a shop that is provably subscribed to that specific webhook topic/address).

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <valid signature for that body under the app's client_secret>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay the same raw body and the same `x-shopify-hmac-sha256` value to the host app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request whose `hmac` still matches (`to_signable_string` only depends on `raw_body`) — [5](#0-4) 
4. `HmacValidator.validate` returns `true` — [6](#0-5) 
5. Any handler invoked via `Registry.process` receives `request.shop == "victim.myshopify.com"` as if Shopify itself asserted this, despite the attacker fully controlling that value.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-59)
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
