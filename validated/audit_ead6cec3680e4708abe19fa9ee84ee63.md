### Title
Webhook `shop-domain` header is trusted but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `ShopifyAPI::Utils::HmacValidator` authenticates the payload bytes alone. The `shop` (from `shopify-shop-domain`/`x-shopify-shop-domain` header) that is later trusted and handed to the app's webhook handler is never part of the signed material.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`to_signable_string` returns only `@raw_body` — no `shop`, `topic`, or `webhook_id` is mixed into the signed string. `HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received signature: [2](#0-1) 

`Registry.process` checks only that this body HMAC is valid, then trusts `request.shop` (parsed straight from the unauthenticated header) to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The binding that should hold is: `hmac == HMAC(secret, body ++ shop ++ topic)` (i.e., the shop the app trusts as the tenant must be cryptographically bound to the same signature as the body). Instead, the actual binding enforced is `hmac == HMAC(secret, body)` while `shop` is taken from an out-of-band header, so:

`(body, shop_A, hmac)` is valid  ⇔  `(body, shop_B, hmac)` is also valid, for any shop_B, because `hmac` only commits to `body`.

Because `api_secret_key` is a single shared app secret used by every shop that installs the app (not a per-shop secret), any entity that can obtain one genuine `(body, hmac)` pair from Shopify — e.g., by installing the app on their own store and receiving Shopify's real webhook delivery — can replay the exact same body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim tenant's domain. The gem raises no error (`Errors::InvalidWebhookError` is only raised on HMAC mismatch) and hands the forged `shop` straight to the handler.

### Impact Explanation
This breaks the cross-tenant boundary the gem is supposed to enforce for webhook delivery: an unprivileged actor who merely holds a legitimate low-privilege presence (their own installed shop) can make the host application process attacker-chosen data (from their own webhook body) as if it belonged to an arbitrary victim tenant (`shop-domain` header value), since the identity ("which shop is this event for") is not bound to the authenticity check. Any app logic keyed off `WebhookMetadata#shop` (updating shop-scoped records, revoking access, disabling billing, uninstall handling, order/customer records, etc.) can be manipulated for a shop the attacker does not own — a cross-tenant access/write primitive achieved purely from the webhook surface, matching the report's "identity binding not covered by the signed material" bug class translated into this gem's webhook verification path.

### Likelihood Explanation
Medium-High: any user can sign up for a Shopify store and install an app built on this gem (no privileged credentials, tokens, or `client_secret` needed), letting them legitimately receive at least one real `(body, hmac)` pair from Shopify for topics they control (e.g., `app/uninstalled`, or any webhook they can trigger from their own store). Replaying that pair with a forged `shop-domain` header is a trivial HTTP request to the app's public webhook endpoint. The only friction is guessing/knowing the victim's `myshopify.com` domain, which is typically public.

### Recommendation
Bind the tenant identity into the signature check rather than trusting the header value: verify that `request.shop` matches the shop associated with the actual delivery context (e.g., cross-check against a shop this app has an active session/webhook registration for), or, at minimum, document/require host applications to independently authenticate the shop (for example by confirming an active installed session exists for that shop) before trusting `WebhookMetadata#shop`, since this gem's `HmacValidator` only authenticates the raw body and cannot vouch for header-supplied identity fields.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `app/uninstalled`), capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent — this HMAC is valid because it is `HMAC(app_secret, body)` and the app secret is shared across all shops.
2. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers unmodified: [4](#0-3) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `@raw_body` against the shared secret: [5](#0-4) 
5. The handler is invoked with `shop: "victim.myshopify.com"` and attacker-controlled body content, even though Shopify never sent this event for `victim.myshopify.com`: [3](#0-2)

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
