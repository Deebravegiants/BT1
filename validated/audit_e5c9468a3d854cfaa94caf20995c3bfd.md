### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, using the app's single, shop-agnostic `api_secret_key`. The `shop` (tenant) attribution used to dispatch the payload to the merchant's handler is taken from the `shopify-shop-domain` HTTP header, which is never included in the signed content and is never validated against Shopify's trusted domain list. Any request bearing a *valid* body+HMAC pair (for any shop using the same app) can be relabelled to any other shop by simply changing the header, because the check that authenticates the request ("HMAC over body, using app secret") and the field the code trusts for tenant identity ("shop" header) are different bindings.

### Finding Description
The identity binding that should hold is: **the shop that the HMAC verifies == the shop the code processes the payload for**. In this gem that equality does not hold.

`Utils::VerifiableQuery#to_signable_string` for a webhook request only returns the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from attacker/Shopify-controlled HTTP headers with no cryptographic binding to the body and no sanitization: [2](#0-1) 

`Registry.process` validates only the HMAC (over the body) and then dispatches to the handler using the unauthenticated `request.shop`: [3](#0-2) 

The HMAC secret used for this validation is the app-wide `Context.api_secret_key` (the same key for every shop that installs the app), not a per-shop secret: [4](#0-3) 

Contrast this with the OAuth callback path in the same gem, where `shop` *is* part of the signed content (`AuthQuery#to_signable_string` includes `shop`): [5](#0-4) 

and with the JWT session-token path, where the shop (`dest` claim) is embedded inside the token payload that is itself covered by the JWT signature: [6](#0-5) 

Webhooks are the outlier: the tenant identifier is carried out-of-band from the authenticated bytes. Because the HMAC secret is shared across every shop that has installed the app, a valid `(body, hmac)` pair generated for shop A remains cryptographically valid when replayed with the `shopify-shop-domain` header rewritten to shop B — `HmacValidator.validate` has no way to detect the substitution since `shop` was never part of `to_signable_string`.

### Impact Explanation
This breaks the equality "shop authenticated == shop the handler acts on," matching the cross-tenant-confusion pattern from the report (an identity check on one side of the system silently diverges from the state acted on by the other side). A handler that trusts `WebhookMetadata#shop` (built directly from `request.shop`) to determine which merchant's local records to update, load a session for, or attribute the event to, can be made to apply shop-A's genuine, signature-valid webhook payload to shop B's tenant context. In a multi-tenant app this is a cross-tenant data-integrity/confusion issue — data from one merchant's store event being recorded, or reacted to, under a different merchant's identity.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (unprivileged) merchant/user of the same app who can trigger and observe one webhook delivery for their own shop (trivial — any merchant can create an order/product and see the resulting webhook body and its valid HMAC, e.g. via their own reverse proxy/logging in front of their receiving endpoint, or Shopify's webhook resend/testing tools). No `api_secret_key`, access token, or privileged account is needed — only the ordinary ability to generate one authentic webhook and resend it with a modified `shop` header, which this gem's `process` method will accept as valid for the impersonated shop.

### Recommendation
Bind the shop (and other dispatch-critical fields such as topic and webhook id) cryptographically to the payload before trusting them, e.g. include `shop`/`topic` in `to_signable_string`, or independently verify `request.shop` against `Utils::ShopValidator` and cross-check it against a shop the app actually has an active session/installation for before invoking the handler, rather than trusting the raw header value used only for routing.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (same `api_secret_key`).
2. Attacker (merchant of shop-a) triggers a real webhook (e.g. `orders/create`) and captures the raw body `B` and header `shopify-hmac-sha256: H` sent to the app's public webhook endpoint (e.g. via their own load balancer/logging in front of the receiver).
3. Attacker resends the exact same body `B` and `H`, but sets `shopify-shop-domain: shop-b.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` in [7](#0-6)  which succeeds because only `B` is signed.
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` in [8](#0-7) , attributing shop-a's event data to shop-b.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-49)
```ruby
        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
```
