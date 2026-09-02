## #Vulnerability found

### Title
Webhook `shop`/`topic`/`webhook_id` identifiers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the `shop`, `topic`, and `webhook_id` values that the handler acts on are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signable content as the raw body only: [1](#0-0) 

Note that `to_signable_string` returns `@raw_body` exclusively — the `shop`, `topic`, and `webhook_id` accessors read directly from HTTP headers (`shopify_header(...)`), which are not part of the signed material.

`Registry.process` validates the request using this signable string and then trusts `request.shop`/`request.topic` verbatim to route the payload and construct the metadata handed to the app's handler: [2](#0-1) 

`HmacValidator.validate` confirms only that the *body* bytes match the HMAC computed with `Context.api_secret_key`: [3](#0-2) 

The identity-binding equality the library implicitly claims is:
`hmac_valid(raw_body) == true` implies `shop_header == "the shop that actually sent this payload"`.

That equality does not hold. The `api_secret_key` for a public app is the **same value for every shop that has installed the app** — it is not a per-shop secret. Therefore any merchant who has installed the app (an ordinary, unprivileged app installer — no admin access token or leaked secret required) legitimately receives real webhook deliveries containing a valid `(raw_body, hmac)` pair for their own shop. Because the `shop-domain`, `topic`, and `webhook-id` headers are excluded from the signed content, that same installer can replay the identical `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting a different `shop-domain` (and/or `topic`) header value. `HmacValidator.validate` will still return `true` (the body bytes and secret are unchanged), and `Registry.process` will dispatch the handler with `WebhookMetadata` carrying the attacker-chosen `shop` value.

### Impact Explanation
Any app built on this library that uses the webhook `shop` value to key session/token lookups, update per-shop state, or authorize per-shop actions (the intended and documented usage of `WebhookMetadata#shop`) can be made to process attacker-supplied data under a victim shop's identity. This is a cross-tenant identity confusion: an unprivileged app installer on shop A can cause the application to believe a payload originated from shop B, without possessing B's access token or any Shopify-side secret. Depending on how the host app consumes the webhook (e.g., app-uninstall/GDPR/orders webhooks that trigger token revocation, data deletion, or state changes keyed by `shop`), this can lead to cross-tenant data corruption or denial of a specific victim tenant's app functionality.

### Likelihood Explanation
The webhook endpoint is a public, unauthenticated HTTP endpoint by design (Shopify calls it over the internet), so no special network position is required. The only prerequisite is that the attacker have legitimately installed the app on any shop (a normal, self-service action available to any Shopify merchant/unprivileged user), from which they can capture at least one genuine `(raw_body, hmac)` pair to replay with a forged `shop-domain` header. No leaked credentials, access tokens, or `api_secret_key` are needed.

### Recommendation
Bind the identifying fields into the signed material, or otherwise require the caller to separately authenticate/associate `shop`/`webhook_id` with a known, registered subscription before trusting them (e.g., cross-check `webhook_id` against a subscription ID previously registered for the specific shop via `Registry.register`, rather than trusting the header value as-is). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must be independently verified by the host application before being used for authorization or data-access decisions.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets it deliver a real webhook, capturing the raw POST body `B` and the `X-Shopify-Hmac-SHA256` header value `H` (a valid signature over `B` under the app's single, shared `api_secret_key`).
2. Attacker sends a new POST to the same webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Request.new` parses headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates only `raw_body` against `H` — validation succeeds.
4. The registered handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, i.e., attacker-controlled body content processed under the victim's shop identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
