The strongest analog to the reported bug class ("field acted on but not covered by the authentication check") that exists in `lib/shopify_api/**` is in the webhook HMAC verification path, not the websocket-method-lookup bug itself.

### Title
Webhook HMAC only signs the raw body, allowing shop/topic impersonation via header substitution - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by calling `Utils::HmacValidator.validate(request)`, but the `Request#to_signable_string` implementation returns only the raw HTTP body — it never includes the `shop`, `topic`, `webhook_id`, or `api_version` values that are read straight from unauthenticated HTTP headers and then trusted for routing and business logic.

### Finding Description
`ShopifyAPI::Webhooks::Request` derives its authenticated fields from HTTP headers, but only the body participates in the HMAC: [1](#0-0) 

`Registry.process` validates the HMAC over that same signable string (body only) and then unconditionally trusts `request.shop` and `request.topic` — both parsed from headers that are outside the HMAC — to route the payload to a handler and to build the `WebhookMetadata` passed to the app's business logic: [2](#0-1) 

The `HmacValidator` itself is generic and only checks whatever `to_signable_string` returns against the shared `Context.api_secret_key`: [3](#0-2) 

The equality the code implicitly assumes is:
`hmac_valid(raw_body) == request_is_authentically_from(shop, topic)`

but the actual binding enforced is only:
`hmac_valid(raw_body) == body_is_authentic`

The `shop-domain`, `topic`, `webhook-id`, and `api-version` header values are never part of the signed content, so they are attacker-controllable independent of whether the HMAC check passes. Any party who can obtain one genuinely Shopify-signed `(body, hmac)` pair — e.g. a webhook delivered by Shopify to their own installed shop, which any store owner naturally receives — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different shop domain (and/or topic) in the headers. `HmacValidator.validate` will still return `true` because it only recomputes the HMAC over the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data originated from the substituted shop/topic.

### Impact Explanation
This breaks the tenant-identity binding the HMAC is meant to provide: the app's webhook handler code (built on this gem's `Registry.process`/`WebhookMetadata`) has no way to distinguish "this body genuinely occurred for this shop/topic" from "this body was replayed under a forged shop/topic," since the gem itself never binds those values to the signature. Depending on what the host app does with `WebhookMetadata#shop` (e.g., looking up the tenant's session/access token, updating tenant-scoped records, processing GDPR/app-uninstalled events), this enables cross-tenant data confusion/injection — one tenant's legitimately-signed webhook traffic can be relabeled to impersonate another tenant.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid `(raw_body, hmac)` pair signed with the app's `client_secret` — obtainable by any merchant who has installed the app and receives normal webhook deliveries for their own shop. No knowledge of `client_secret` is needed to perform the replay/header-substitution itself, only network access to the app's public webhook endpoint. This is a plausible, low-privilege attack path (a legitimate, unprivileged app user replaying their own captured webhook with modified headers).

### Recommendation
Include the identity-bearing fields (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the HMAC-signed content, or otherwise cryptographically bind them to the body (e.g., by validating them against a value embedded in the signed payload, or requiring the host app to cross-check `request.shop` against a shop the app already has a valid session/access token for) before trusting them in `Registry.process`.

### Proof of Concept
1. Configure the app with `ShopifyAPI::Context` and register a webhook handler for topic `orders/create`.
2. Legitimately receive one real webhook from Shopify for `shop-a.myshopify.com` with topic `orders/create`, capturing the raw body `B` and its `X-Shopify-Hmac-Sha256` header `H`.
3. Send a new HTTP request to the app's webhook endpoint with the same body `B` and same `hmac-sha256` header `H`, but with `shopify-shop-domain` set to `shop-b.myshopify.com` (a different tenant).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only validates `B` against `H` — see `to_signable_string` returning `@raw_body` at [4](#0-3) . The handler is then invoked with `shop: "shop-b.myshopify.com"` despite the payload never being authenticated for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
