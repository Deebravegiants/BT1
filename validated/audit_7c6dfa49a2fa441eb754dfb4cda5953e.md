### Title
Webhook shop, topic, and webhook-id headers are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable value using only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — all of which are trusted and forwarded unchanged to the application's webhook handler — come from HTTP headers that are never included in the HMAC computation.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the HMAC exclusively over that signable string and compares it to the `hmac-sha256` header: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching the request to the registered handler, then constructs the `WebhookMetadata` directly from the unauthenticated `shop`, `topic`, `webhook_id`, and `api_version` headers: [3](#0-2) 

`request.shop` and `request.topic` are read straight from headers with no cross-check against the signed payload: [4](#0-3) 

This breaks the intended identity binding `hmac == HMAC(body)` versus the actual trust decision the host application makes, which is `handler.handle(shop: header["shop-domain"], topic: header["topic"], body)`. Because the header fields are not part of the HMAC input, any request whose body matches one for which a valid HMAC can be produced (for example, the fixed-shape mandatory compliance webhooks `shop/redact`, `customers/redact`, `customers/data_request`, or any webhook body an attacker's own installed app instance genuinely receives) can be replayed with the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers rewritten to arbitrary values, and `Utils::HmacValidator.validate` will still return `true`. The host application's handler receives a `WebhookMetadata` object that looks authentic (valid HMAC) but whose `shop`/`topic` attribution is fully attacker-controlled.

### Impact Explanation
An unprivileged internet user who can obtain any valid `(body, hmac)` pair signed with the app's `api_secret_key` — which they can generate themselves for their own installed shop, since HMAC only covers the body — can forge webhook deliveries claiming to originate from a different `shop` domain or a different `topic` than what Shopify actually sent. If the host application's webhook handlers key any per-tenant action (data updates, redaction, deprovisioning, GDPR redaction flows) off `WebhookMetadata#shop` without independently confirming the shop is legitimate for that webhook, this enables cross-tenant data manipulation, e.g. triggering `customers/redact`/`shop/redact` handling against a victim shop, or injecting fabricated order/customer data attributed to another merchant.

### Likelihood Explanation
Exploitation requires only the ability to send an arbitrary HTTP POST to the app's public webhook endpoint plus one legitimately-signed `(body, hmac)` pair, which is trivially obtainable by any developer who installs the target app on their own store and captures one of its own webhook deliveries (or the fixed-body mandatory compliance webhooks). No access token, `client_secret`, or privileged account is required, and the header rewrite is possible on the raw HTTP request before it reaches this gem's `Request.new`.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable string, or otherwise cryptographically bind them to the body before validating, e.g. compute `to_signable_string` over a canonical concatenation of the headers and the raw body rather than the raw body alone, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` already binds `shop` into its signed payload.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com` and capture one legitimate webhook delivery, e.g. `customers/redact` with body `{}` and its valid `x-shopify-hmac-sha256` header (or independently compute the HMAC for `body = "{}"` for any of the three mandatory topics, whose payload shape is fixed and predictable).
2. Replay the request to the same app endpoint, keeping `body` and `x-shopify-hmac-sha256` unchanged, but replacing `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks the body-derived HMAC.
4. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches to the handler with `shop: "victim.myshopify.com"`, causing the application to act on the victim's tenant data using a forged, HMAC-"validated" webhook.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
