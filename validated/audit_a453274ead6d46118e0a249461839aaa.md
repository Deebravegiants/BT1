### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` and compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header value. [1](#0-0) 

`Request#to_signable_string` is defined to return only the raw request body: [2](#0-1) 

However, the `shop` and `topic` values that the registry subsequently uses to route the payload and identify the tenant are pulled straight from unauthenticated headers, not from the signed payload: [3](#0-2) 

`HmacValidator.validate` and `validate_signature` only ever look at `verifiable_query.hmac` and `verifiable_query.to_signable_string` — they never touch `shop`, `topic`, `webhook_id`, or `api_version`: [4](#0-3) 

`Registry.process` then constructs `WebhookMetadata` (tenant-identifying data passed to the host app's handler) directly from these unauthenticated headers: [1](#0-0) 

This breaks the identity binding `authenticated_bytes == acted_upon_shop`: the HMAC only proves the *body* came from a holder of `api_secret_key` (i.e., genuinely from Shopify, for *some* shop/topic), it proves nothing about which shop or topic that body belongs to. Contrast this with `Auth::Oauth::AuthQuery`, where `shop` is explicitly included in `to_signable_string` and is therefore bound to the signature: [5](#0-4) 

### Impact Explanation
An unprivileged internet user who controls any Shopify store that installs the target app (e.g., a free development/trial store, obtainable by anyone) legitimately receives real, correctly HMAC-signed webhook deliveries for their own store. Because the signature covers only the raw body and not `shop-domain` or `topic`, the attacker can capture one such legitimately-signed `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic` header) with the value of a victim shop. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` forwards `shop: request.shop` (the attacker-chosen victim shop) and `topic: request.topic` to the app's registered handler as if the event genuinely originated from and pertains to the victim tenant. Any host-application logic that trusts `WebhookMetadata#shop`/`#topic` for tenant-scoped decisions (looking up sessions, updating per-shop state, billing, uninstall/app-status changes, etc.) can be manipulated cross-tenant by an attacker with no relationship to the victim shop and no possession of the app's `client_secret` or access tokens — this is a cross-tenant identity-binding failure in the gem itself, not merely "trusting the host app."

### Likelihood Explanation
Any developer/attacker can register their own free Shopify store, install the target app, and receive real webhook deliveries signed with the app's shared secret. Swapping the `shop-domain`/`topic` header on a replayed request requires no cryptographic material and no privileged access — only observing traffic to one's own endpoint. Given webhook processing is a documented, commonly used code path (`docs/usage/webhooks.md`), likelihood of exposure is high wherever the host app relies on `WebhookMetadata#shop`/`#topic` for tenant-sensitive logic.

### Recommendation
Bind `shop`, `topic` (and ideally `webhook_id`/`api_version`) into the value that is HMAC-verified, e.g. by including the relevant headers in `to_signable_string`, or by cross-checking `request.shop` against an explicit allow-list / an already-established session for that shop before invoking the handler, rather than trusting header-sourced values purely because the raw body passed HMAC validation.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a genuine webhook delivery: body `B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`== B`) and matches `H` — validation passes (see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-31`).
4. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the payload never originated from or pertains to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
