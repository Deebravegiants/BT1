### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying the HMAC over the raw request body, then hands the handler a `shop` value that is read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header. The HMAC never covers that header, so verifying the body's authenticity does not verify which shop the event is claimed to be for.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `HmacValidator.validate` computes/compares the HMAC exclusively against that signable string: [2](#0-1) 

Meanwhile `Request#shop` is parsed directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, a field that plays no role in `to_signable_string`: [3](#0-2) 

`Registry.process` treats HMAC success as proof the whole request "did indeed come from Shopify" for this shop, then forwards `request.shop` unmodified into `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The documentation reinforces this: it states `Registry.process` "will verify the request did indeed come from Shopify" and describes `data.shop` as simply "The shop domain of the webhook," without noting that this field is unauthenticated relative to the HMAC.

The equality that should hold is: `shop bound by HMAC == shop delivered to handler`. In fact: `shop verified by HMAC (none — body only) != shop passed to handler (raw header value)`. Unlike `Auth::Oauth::AuthQuery`, where `shop` is part of the signed parameter set consumed by `to_signable_string` (`code`, `host`, `shop`, `state`, `timestamp`), the webhook path's `shop` is completely outside the signed payload: [5](#0-4) 

Because any store owner can install a public app for their own store (no special privilege required) and thereby cause Shopify to emit legitimately HMAC-signed webhooks for arbitrary body content under their own shop domain, that unprivileged actor can capture such a request and resend it with the `shop-domain` header rewritten to a different (victim) shop's domain. The HMAC check still passes (it only validates `@raw_body`, unchanged), and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain, feeding attacker-controlled body content into whatever the app does with `data.shop` (e.g., writing to that shop's records, keying background jobs, or session/data association) — a cross-tenant identity break driven purely by an unauthenticated header value.

### Impact Explanation
This breaks the identity binding `shop authenticated == shop the data is attributed to`. Any app that uses `data.shop` from `WebhookMetadata` (as the gem's own documentation instructs) to key merchant-scoped state can be made to associate attacker-supplied webhook body content with an arbitrary victim shop domain, since the shop field is never authenticated by the gem — only the byte contents of the body are. This is a cross-tenant data-integrity/confidentiality risk consistent with the "cross-tenant access" impact category, achieved by an unprivileged internet user (any merchant who can install/trigger events on a public app) with no access to the app's `client_secret`, access tokens, or TLS interception.

### Likelihood Explanation
Likelihood is significant because: (1) obtaining a legitimately-signed webhook (body + HMAC) requires nothing more than installing the app on any store and generating an event that the app subscribes to — no credential theft; (2) replaying an HTTP request with a modified header while preserving the byte-identical body is a completely standard proxy/replay operation; (3) the gem provides no safeguard, cross-check, or warning that the `shop` field is unauthenticated — its documentation and API actively encourage trusting `data.shop`.

### Recommendation
Bind the shop identity to the verified payload rather than trusting an unauthenticated header. Options: incorporate a per-shop or per-installation secret/session lookup keyed only by verified data (e.g., cross-check the `shop-domain` header against the shop registered for the given `webhook-id`, or require callers to separately validate `shop` against their own session store before trusting it), or extend `to_signable_string`/signature verification to cover the shop domain and other identifying headers so that tampering with them invalidates the HMAC. At minimum, the documentation should explicitly warn that `WebhookMetadata#shop` is not covered by HMAC verification and must not be trusted for tenant-scoping decisions without additional server-side verification.

### Proof of Concept
1. Attacker installs the target (public) Shopify app on their own store `attacker.myshopify.com` and triggers a subscribed webhook topic (e.g., `orders/create`), causing Shopify to POST a body `B` with a valid `x-shopify-hmac-sha256` computed over `B` using the app's real `api_secret_key`.
2. Attacker captures this request (`B`, valid HMAC over `B`).
3. Attacker resends the identical body `B` and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `HmacValidator.validate` recomputes the HMAC over `@raw_body` (`B`) only, which still matches — verification passes: [6](#0-5) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)`, causing the app to process attacker-controlled body content as if it belonged to `victim.myshopify.com`.

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
