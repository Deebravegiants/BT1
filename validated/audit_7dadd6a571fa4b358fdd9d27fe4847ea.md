### Title
Webhook shop identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only, while the `shop` field that identifies which merchant/tenant the webhook belongs to is read from an unsigned HTTP header. `Registry.process` trusts this unsigned `shop` value when dispatching the webhook payload to the app's handler, so the HMAC never actually binds "this payload is authentic" to "this payload belongs to this shop."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is not part of the signed material at all: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, so it only ever validates the body/signature pair, never the shop header: [3](#0-2) 

`Registry.process` performs this HMAC check and then immediately trusts `request.shop` (and the rest of the unsigned metadata) to build the object handed to the app's webhook handler, with no cross-check that the shop matches anything tied to the signature: [4](#0-3) 

This is the same class of bug as the CEI-ordering report: an identity field (`shop`) is *acted on* by the code but is not *covered* by the integrity check (HMAC) that's supposed to authenticate the request. In `Auth::Oauth::AuthQuery`, the gem's authors clearly understood this requirement and explicitly fold `shop` into the signed string: [5](#0-4) 

but the same discipline was not applied to `Webhooks::Request`.

Practically: any body+HMAC pair that is valid for shop A's webhook is *also* valid for a request that claims (via the header) to be shop B, because the signature never covered the shop field. An attacker who can obtain one genuine, validly-signed webhook payload for the app (e.g. by installing the app on their own store or capturing a webhook they control) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header to name a victim shop. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming to be from the victim shop: [6](#0-5) 

If the host application uses `data.shop` to look up records, update state, or authorize actions per-tenant (the documented and expected use of `WebhookMetadata#shop`), this allows an unprivileged attacker to inject attacker-controlled data into another merchant's tenant context — a cross-tenant boundary violation rooted entirely in this gem's webhook verification method.

### Impact Explanation
This breaks the identity binding "HMAC-authenticated payload == authenticated for shop X." An attacker with no privileges beyond running their own Shopify store (or any store where they can trigger a webhook) can forge the `shop` identity on an otherwise-legitimate signed webhook and have it accepted as authentic for a different, victim tenant. This is a cross-tenant access class issue as defined in scope.

### Likelihood Explanation
Medium-to-High: the attacker needs no privileged credentials — only a Shopify store they control that has the target app installed (or any mechanism to obtain one genuine signed body+HMAC pair, e.g. via a topic with a stable/predictable body). Replaying the same body with a different `shop` header is trivial once captured, since nothing in `Registry.process`/`HmacValidator.validate` ties the signature to the header value.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed material for webhook requests, mirroring the pattern already used in `Auth::Oauth::AuthQuery#to_signable_string`. At minimum, `Registry.process` should independently verify that the `shop` in the request corresponds to a shop the app actually has installed/has a stored session for before dispatching to a handler, rather than trusting the unauthenticated header value directly.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with raw body `B` and a valid `x-shopify-hmac-sha256` header `H` (computed by Shopify over `B` using the app's `client_secret`).
2. Attacker captures `(B, H)` (e.g., by pointing the webhook delivery at a proxy they control, or simply owning the store that receives it).
3. Attacker sends a POST to the app's webhook endpoint with the same raw body `B`, the same `H` header, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` passes because it only checks `H` against `B`: [7](#0-6) 
5. `Registry.process` dispatches the handler with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com`, even though the payload was never issued for that shop: [4](#0-3)

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
