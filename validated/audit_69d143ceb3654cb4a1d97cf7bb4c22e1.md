### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) headers are trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers, but `#to_signable_string` — the value that is actually HMAC-verified — returns only `@raw_body`: [1](#0-0) 

`Registry.process` verifies only that the body's HMAC matches, then immediately trusts `request.shop` and forwards it to the app's handler as the tenant identifier, with no binding between the verified bytes (the body) and the acted-upon field (`shop`): [2](#0-1) 

`HmacValidator.validate` confirms the check is body-only — it never incorporates the `shop`, `topic`, or `webhook_id` headers into the signable string it verifies: [3](#0-2) 

The identity binding that should hold is: `hmac-signed bytes == bytes that determine which shop a webhook is attributed to`. In this implementation that equality does not hold: `hmac-signed bytes = raw_body` while `attributed shop = header["shopify-shop-domain"]`, which is disjoint from the signed content. Because a single app's `client_secret` (`Context.api_secret_key`) is shared and used to sign webhooks for *every* shop that installs the app, an attacker who installs the app on their own (attacker-owned) shop can receive a genuinely-signed `(raw_body, hmac)` pair from Shopify for a webhook whose body content they control (e.g. by editing a product/order on their own store). They can then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass, because it only checks the body against the secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) body originated from the victim shop.

The gem's own documentation reinforces the false sense of security, stating that `Registry.process` "will verify the request did indeed come from Shopify" without qualifying that the shop attribution itself is unauthenticated: [4](#0-3) 

This is the direct analog of the LPFarming bug class: just as `pool.lpToken.balanceOf(address(this))` conflated attacker-donated tokens with tracked deposits because the accounting field wasn't bound to the deposit path, here the `shop` field used for tenant attribution is not bound to (not covered by) the cryptographic check that is supposed to authenticate the whole request.

### Impact Explanation
This breaks the cross-tenant boundary that the gem is trusted to enforce: consuming applications rely on `WebhookMetadata#shop` (sourced from `Request#shop`) as the authenticated tenant identifier to route data, update per-shop records, or trigger side effects. An attacker who is merely an unprivileged internet user with respect to *other* merchants — but a legitimate installer of the app on their own store — can forge webhook deliveries that are misattributed to any other shop domain, since nothing after HMAC validation checks that the `shop` header is consistent with a value bound by the signature. Depending on how the host application consumes `data.shop` (e.g. looking up/activating a session, writing per-shop state, or triggering shop-scoped side effects), this enables cross-tenant data injection or corruption without ever compromising the target shop's own token or credentials.

### Likelihood Explanation
Exploitability requires only that the attacker be able to install the target app on a store they control (a normal, permitted action for any merchant/developer testing an app) and be able to send an arbitrary HTTP request to the app's public webhook endpoint with modified headers — both are within reach of an unprivileged actor and require no access to the app's `client_secret`, access tokens, or any victim credentials.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the HMAC-verified material, or otherwise cryptographically tie the accepted tenant identity to the signed payload rather than trusting an independently-supplied header. At minimum, `Utils::VerifiableQuery#to_signable_string` for webhook requests should incorporate the `shop` header (mirroring how Shopify's own webhook signature is computed over the full raw body, but requiring the consuming app to independently confirm the `shop-domain` header corresponds to a shop with an active, previously-established installation/session before trusting it) and the library's documentation should be corrected to state explicitly that only the body — not the shop/topic/webhook-id headers — is authenticated by HMAC verification, so integrators know they must independently validate shop attribution against their own installed-shop records.

### Proof of Concept
1. Attacker registers/installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook (e.g. `orders/create`) on their own store, capturing the genuine `raw_body` and `x-shopify-hmac-sha256` value Shopify sends — this HMAC is valid because it is computed with the app's single shared `client_secret`: [5](#0-4) 
3. Attacker POSTs to the app's public webhook route with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the mismatched headers/body combination since header validation only checks presence, not correlation with the body: [6](#0-5) 
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it hashes only `raw_body`: [7](#0-6) 
6. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-crafted body, believing it is an authenticated webhook from the victim's store.

**Note on completeness:** I was unable to locate a separate `WebhookMetadata` class file in the indexed portion of the codebase (only a reference in `webhook_handler.rb` was found) or downstream consumption examples beyond the documentation snippet, so I cannot cite the exact `WebhookMetadata` struct definition. If the maintainers want a more precise trace of how `data.shop` is consumed inside this gem versus purely by host applications, a full Devin session with repository access would be needed to confirm any additional internal use of `Request#shop` beyond what is exposed here.

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

**File:** lib/shopify_api/webhooks/request.rb (L46-63)
```ruby
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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
```
