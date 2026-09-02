### Title
Webhook `shop` (tenant) identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC computed by `Utils::HmacValidator` proves nothing about which shop the webhook is for. The `shop` value that `Registry.process` hands to the app's handler as the trusted tenant identifier is read straight from the unauthenticated `x-shopify-shop-domain` header. Any user who can generate one genuine `(body, hmac)` pair (e.g. by installing the app on their own store and receiving a real webhook) can replay that exact pair to the target app's webhook endpoint while swapping the shop header to name a different, victim shop. The signature still validates because the body — not the shop — is what's signed, and the same `api_secret_key` is shared across all shops that install the app.

### Finding Description
`Request#hmac` and `Request#to_signable_string` only ever reference `@raw_body`: [1](#0-0) [2](#0-1) 

Meanwhile `shop` is read from a header that is never mixed into the signable string: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e. the body) and compares it against the received `hmac`: [4](#0-3) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then forwards the unauthenticated `request.shop` straight into `WebhookMetadata`, which the app's handler is documented to use as the merchant/tenant identity for the payload: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `hmac-verified bytes == bytes the app trusts as belonging to shop X`. Here that equality is broken — the HMAC verifies the body only, while `shop` (the tenant-scoping field) is taken from bytes that were never verified at all. This exactly matches the bug-class pattern of "a field acted on but not covered by the HMAC."

### Impact Explanation
Because the app's `api_secret_key` is the same for every shop that installs the app, any low-privilege actor who installs the app on their own (even free/trial) store legitimately receives real, correctly-signed `(body, hmac)` webhook deliveries for that store. That same signed pair remains valid for any other shop name, because the shop identity was never part of what got signed. By replaying the captured body/HMAC to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain, the attacker gets the app to process attacker-supplied webhook data as though it belongs to a different, arbitrary tenant. This is a cross-tenant data-confusion/injection primitive scoped squarely at the credential/tenant boundary the gem is responsible for enforcing (Critical: cross-tenant access).

### Likelihood Explanation
No secret key, access token, or privileged account is required — only a normal app installation (something an unprivileged internet user can obtain on a free trial store) plus the ability to POST to the app's public webhook URL, which by Shopify's design must accept unauthenticated inbound POSTs verified solely by HMAC. The replay itself is trivial (same body, same hmac, different header value).

### Recommendation
Include the shop domain (and ideally topic/webhook_id) inside the HMAC-signed material, or otherwise cryptographically bind the shop identity to the signed body before trusting `request.shop` for tenant-scoped processing. At minimum, `Registry.process`/`WebhookMetadata` construction should not treat the shop header as authenticated just because the body-only HMAC passed.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid signature over `B` using the app's shared `api_secret_key`).
2. Attacker sends a POST to the app's public webhook endpoint with the same raw body `B` and the same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` still matches `H` for body `B` (per `lib/shopify_api/webhooks/request.rb`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which returns `true` because only the body is checked (per `lib/shopify_api/utils/hmac_validator.rb`).
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)` and invokes the app's handler, which now processes attacker-supplied data as if it authentically originated from `victim.myshopify.com`.

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
