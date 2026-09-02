### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, then dispatches the handler using the `shop` value taken directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header — a value that is **not** included in the signed payload. This breaks the identity binding `HMAC-verified bytes == tenant-attributed bytes`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively over that signable string and compares it against the `hmac` field, using the app-wide `Context.api_secret_key`: [2](#0-1) 

But `Registry.process` uses `request.shop` — parsed straight from the `shopify-shop-domain` header, which is never part of `to_signable_string` — to build the `WebhookMetadata` that is handed to the app's handler: [3](#0-2) [4](#0-3) 

The equality the gem *should* enforce is: `shop attributed to the event == shop cryptographically bound to the signed bytes`. Instead it enforces: `body bytes are signed by the app secret` AND separately, unauthenticated: `shop = header value`. Since the HMAC secret (`Context.api_secret_key`) is a single, app-wide value shared across every installed shop (not scoped per-tenant), any actor who can obtain one valid `(raw_body, hmac)` pair — trivially available to any merchant who installs the app on their own store and receives real webhooks (e.g. a static/predictable body such as `{}` for topics like `app/uninstalled`) — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still returns `true` because it never looked at the header, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler (which typically performs shop-scoped side effects such as marking a shop uninstalled, deleting stored sessions/tokens for a shop, or updating shop-scoped records) can be triggered under an arbitrary victim shop identity by an unprivileged actor who only needs to be a legitimate (even free-tier) installer of the app for their own store. This satisfies the Critical "cross-tenant access" impact bar, since the attacker can make the host application act on behalf of, or destroy state belonging to, a shop they do not own or operate — without ever needing the app's `client_secret`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
Likelihood is high for any topic whose legitimate body is static, predictable, or fully attacker-influenced (many mandatory/compliance topics and simple lifecycle topics like `app/uninstalled` have minimal or empty bodies), because the attacker can generate a valid `(body, hmac)` pair for themselves and then simply swap the `shop-domain` header value on replay — no cryptographic secret is ever required. For topics whose body varies by real shop content it is somewhat lower, but the vulnerability is systemic across all topics because the shop identity is architecturally excluded from the signed payload.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the material verified by the HMAC check, or otherwise cryptographically/contextually tie the `shop-domain` header to the same request being authenticated — e.g., include the relevant Shopify headers in the value passed to `HmacValidator`, or require the caller to supply/verify an expected shop out-of-band (such as matching against the shop tied to the app's known installed sessions) before trusting `request.shop` for dispatch.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and captures one legitimate webhook delivery for a topic with a static/minimal body (e.g. `app/uninstalled`, body `{}`), noting the `x-shopify-hmac-sha256` header value that was computed by Shopify with the app's shared secret over that body.
2. Attacker replays a POST to the app's webhook endpoint with the identical raw body `{}` and identical `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: app/uninstalled`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the body against the secret — this passes, since the body/HMAC pair is unchanged from step 1: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host application to perform shop-scoped actions (e.g. de-provisioning, session deletion) against the victim tenant, which the attacker does not control.

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
