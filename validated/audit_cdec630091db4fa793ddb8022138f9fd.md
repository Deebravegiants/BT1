## Title
Webhook shop domain and topic are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives its HMAC-signable content solely from the raw request body, while the `shop`, `topic`, and `webhook_id` fields — read straight from unauthenticated HTTP headers — are used unchecked to route and label the webhook event. Any party that has legitimately received one real webhook for their own shop (i.e. any merchant who installs the host app — no `api_secret_key` or access token required) can replay that same signed body while swapping the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`) headers, and the gem's HMAC check will still pass.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are pulled directly from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` and compares it to the `hmac-sha256` header value — it never touches `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust the header-derived `topic` (for handler dispatch) and `shop` (propagated into `WebhookMetadata`) without any further verification that they correspond to the shop/topic the body was actually signed for: [4](#0-3) 

The broken identity binding, expressed as an equality that the code assumes but never checks:
`HMAC(raw_body) is valid` ⇏ `request.shop == the shop that body was actually generated for`.

Because the signature only binds the body bytes, any legitimate (unprivileged) merchant who has installed the app receives real `(raw_body, hmac)` pairs from Shopify for their own store. They can capture such a pair and re-POST the identical body to the app's webhook endpoint while substituting a different shop's domain in `X-Shopify-Shop-Domain` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`). `HmacValidator.validate` recomputes the HMAC over the (unchanged) body and it matches, so `Registry.process` accepts the request, dispatches it to whatever handler the forged `topic` selects, and calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain — all without ever needing the app's `client_secret`.

### Impact Explanation
This is a cross-tenant integrity issue: a host application relying on `ShopifyAPI::Webhooks::Registry.process`/`WebhookMetadata#shop` to determine which tenant's data to act on can be tricked into processing attacker-fabricated events "on behalf of" a shop the attacker does not own or control, using only a webhook the attacker legitimately received for their own store. Depending on what the host app's webhook handlers do (e.g. update local records, trigger uninstall/reinstall side effects, alter billing state, or process `app/uninstalled`-style logic) keyed off `data.shop`, this enables cross-tenant data manipulation.

### Likelihood Explanation
Moderate-to-high: any user who can install the target app on a real Shopify store obtains genuine `(body, hmac)` pairs and can immediately replay them with a spoofed shop/topic header — no access token, refresh token, or `client_secret` is required, and no privileged account is needed.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-signable content or otherwise verify header authenticity — e.g., require the caller to record which shop/topic combination it expects for a given signed body, and reject processing if the header-derived `shop` does not match the shop the app already has an active session/access token for. At minimum, document and enforce that consumers must independently validate `WebhookMetadata#shop` against their known install list before trusting it.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; Shopify sends a legitimate webhook with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid signature of `B`) and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Capture `B` and `H`.
3. POST the same body `B` and header `H` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally change `X-Shopify-Topic`).
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `B` only, which still equals `H`, so validation succeeds: [5](#0-4) 
5. `Registry.process` invokes the topic's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to act as though the event originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
