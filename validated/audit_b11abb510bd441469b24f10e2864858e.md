This confirms the vulnerability. The `Registry.process` method at `lib/shopify_api/webhooks/registry.rb:188-200` validates the HMAC over the request, then passes `request.shop` — sourced from an unauthenticated header — directly to the handler as the tenant identifier, without that field being covered by the signature.

### Title
Webhook tenant attribution (`shop` domain) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw HTTP body [1](#0-0) , while the `shop` value that is later trusted and forwarded to the app's webhook handler is read straight from the `shopify-shop-domain` HTTP header, which is not part of the signed content [2](#0-1) . `Registry.process` verifies only that the body's HMAC is valid for the app's shared `api_secret_key`, then immediately trusts `request.shop` to construct `WebhookMetadata` for tenant-specific processing [3](#0-2) .

### Finding Description
The binding that should hold is: `shop (verified by HMAC) == shop (acted upon by the handler)`. Instead, the HMAC only binds `raw_body`, and `shop` is taken from a separate, unsigned header [4](#0-3) . Because Shopify webhooks for a given app are all signed with the *same* `api_secret_key` regardless of which shop/tenant sent them, any (raw_body, hmac) pair that is valid for one shop's webhook is equally valid HMAC-wise for a POST claiming to be from a different shop — the validator in `Utils::HmacValidator.validate` never inspects the `shop` field at all [5](#0-4) .

An attacker who legitimately installs the target app on their own store (any developer can do this for a public app) will receive genuinely-signed webhook deliveries. By replaying the exact `raw_body` and `x-shopify-hmac-sha256` value they received, but substituting the `x-shopify-shop-domain` header with a victim shop's domain, the forged request still passes `Utils::HmacValidator.validate` in `Registry.process` [6](#0-5) , and the handler is invoked believing the data legitimately belongs to the victim shop.

### Impact Explanation
This is a cross-tenant confusion vulnerability: the app's webhook handler acts on `data.shop` (used by app developers to store/attribute data, trigger shop-scoped side effects, or to fulfil mandatory compliance topics such as `customers/redact`, `shop/redact`, `customers/data_request`) believing it to be authenticated, when in fact the tenant attribution is fully attacker-controlled. Depending on how the hosting app implements its handler (as documented and expected by this gem — see `docs/usage/webhooks.md`), this can lead to data being written, deleted, or disclosed under the wrong shop's identity, i.e. cross-tenant access, which meets the Critical impact bar for cross-tenant access.

### Likelihood Explanation
Likelihood is high for any attacker who can install the app (a normal, unprivileged action for public apps) on a store they control: they need no secrets, tokens, or special access to capture a validly-signed webhook and replay it with a modified shop-domain header against the app's own webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the value that is verified, or otherwise cryptographically/authoritatively bind the header-derived `shop` to the payload before trusting it — e.g., require the caller to independently confirm that `request.shop` corresponds to a shop with an active installation/session for this app, rather than trusting the header outright, or have `HmacValidator`/`Request` fold the header value into `to_signable_string` for the comparison basis it uses when the header is going to be trusted as tenant identity downstream.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com`, obtaining a store that receives genuine webhooks from Shopify signed with the app's `api_secret_key`.
2. Attacker captures a legitimate webhook HTTP request (e.g. via a debugging proxy/ngrok) for `attacker-shop.myshopify.com`, noting the raw body and the `x-shopify-hmac-sha256` header value.
3. Attacker crafts a new POST request to the app's webhook endpoint with the identical raw body and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and calls `ShopifyAPI::Webhooks::Registry.process`; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the shared secret [7](#0-6) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [8](#0-7) , causing the app to act on attacker-supplied data believing it originates from the victim shop.

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
